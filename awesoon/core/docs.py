
import re
from uuid import uuid4
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from awesoon.core.models.doc import doc

db = DatabaseApiClient()


def generate_document(shop_id, app_name):
    """
    Retrieve and concatenate shop information
    Args:
        shop_id: unique shop indentifier to retrieve information from
    Return:
        A string stripped of extraneous characters that is ready to be split
    """
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    policies = queries["shopify"].get_shop_policies(shop["shop_url"], shop["access_token"])
    products = queries["shopify"].get_shop_products(shop["shop_url"], shop["access_token"])
    categories = queries["shopify"].get_shop_categories(shop["shop_url"], shop["access_token"])
    document = re.sub(r"[{}']", "", str({
        "policies": policies,
        "products": products,
        "categories": categories
    }))

    return document


def split_document(document):
    """Split a single document string into chunks
    TODO: Fine tune the chunking parameters
    Args:
        document: string to split
    Returns:
        List of chunked texts
    """

    text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
    documents = text_splitter.split_text(document)
    return documents


def generate_document_embedding(documents):
    """Generate a single document embedding
        Args:
            documents: list of chunked texts
        Returns:
            Embedding of chunked texts
    """
    openai = OpenAIEmbeddings()
    embeddings = openai.embed_documents(documents)
    return embeddings


def shop_compute(shop_id, args):
    """
    Send shop information to the database
    Args:
        shop_id: unique shop indentifier to retrieve information from
        args: includes the filter params (app_name)
    Return:
        Returns success message
    """
    app_name = args["app_name"]
    document = generate_document(shop_id, app_name=app_name)
    documents = split_document(document)
    embedding = generate_document_embedding(documents)
    scan_version_id = uuid4().hex
    data = [doc(
        document=documents[i], embedding=embedding[i], docs_version=scan_version_id) for i in range(len(documents))
    ]
    print(data[0])
    print(data[1])
    for i in range(len(documents)):
        db.add_doc(shop_id, data[i])

    return True
