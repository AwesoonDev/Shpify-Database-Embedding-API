from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.shopify.policy import ShopifyQuery
from json import dumps
import re
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from uuid import uuid4
from flask_restx import Namespace, fields, marshal
from requests.exceptions import HTTPError
from dotenv import load_dotenv
load_dotenv()

db = DatabaseApiClient()

ns = Namespace(
    "shops", "This namespace is resposible for retrieving and storing the shops info.")
doc_model = ns.model(
    "doc",
    {
        "document": fields.String(),
        "embedding": fields.List(fields.Float, required=False, default=[]),
        "docs_version": fields.String()
    },
)

TEMPLATE = "The following is a friendly conversation between a customer " \
            "and an AI customer assistant. The AI is helpfull and not so much descriptive. " \
            "The AI should only talk about things relating to the products and policies. " \
            "Respond with answeres as short as possible.\n Given the shop policies:"


def get_shop_policies(shop_id):
    shop = db.get_shop(shop_id)
    return ShopifyQuery.get_shop_policies(shop["shop_url"], shop["access_token"])

def get_shop_products(shop_id):
    shop = db.get_shop(shop_id)
    return ShopifyQuery.get_shop_products(shop["shop_url"], shop["access_token"])

def get_shop_categories(shop_id):
    shop = db.get_shop(shop_id)
    return ShopifyQuery.get_shop_categories(shop["shop_url"], shop["access_token"])

def generate_shop_prompt_by_policies(policies):
    prompt = f"{TEMPLATE}\n\n"
    for i, policy in enumerate(policies, start=1):
        prompt = prompt + f"Policy {i}: {policy}"
    return prompt

def generate_documents(shop_id):
    shop = db.get_shop(shop_id)
    policies = ShopifyQuery.get_shop_policies(shop["shop_url"], shop["access_token"])
    products = ShopifyQuery.get_shop_products(shop["shop_url"], shop["access_token"])
    categories = ShopifyQuery.get_shop_categories(shop["shop_url"], shop["access_token"])
    document_str = re.sub(r"[{}']", "", str({
        "policies": policies,
        "products": products,
        "categories": categories 
    }))

    text_splitter = TokenTextSplitter(chunk_size=2000, chunk_overlap=400)
    documents = text_splitter.split_text(document_str)
    return(documents)

# Generate a single document embedding
# Args:
#   document: list of chunked texts
# Returns:
#   Embedding of chunked texts
def generate_document_embedding(documents):
    # Initialize.
    openai = OpenAIEmbeddings()
    # Embed. Argument is a list of texts
    embeddings = openai.embed_documents(documents)
    return embeddings

def shop_compute(shop_id):
    documents = generate_documents(shop_id) 
    embedding = generate_document_embedding(documents)

    data = [{"document": documents[i], "embedding": embedding[i], "docs_version": uuid4().hex} for i in range(len(documents))]
    responses = []
    for i in range(len(documents)):
        try:
            response = db.send_docs(shop_id, marshal(data[i], doc_model))
            responses.append(response)
        except HTTPError as ex:
            responses.append(ex)

    return responses