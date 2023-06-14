from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.shopify.policy import ShopifyQuery
from json import dumps
from langchain.embeddings import OpenAIEmbeddings
from uuid import uuid4
from flask_restx import Namespace, fields, marshal
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

def generate_document(shop_id):
    shop = db.get_shop(shop_id)
    policies = ShopifyQuery.get_shop_policies(shop["shop_url"], shop["access_token"])
    products = ShopifyQuery.get_shop_products(shop["shop_url"], shop["access_token"])
    categories = ShopifyQuery.get_shop_categories(shop["shop_url"], shop["access_token"])
    document = dumps({
        "policies": policies,
        "products": products,
        "categories": categories 
    })
    return(document)

# Generate a single document embedding
# Args:
#   document: string. Single text to embed.
# Returns:
#   Single embedding
def generate_document_embedding(document: str):
    # Initialize.
    openai = OpenAIEmbeddings()
    # Embed. Argument is a list of texts, so we wrap document as a list with 1 element
    embeddings = openai.embed_documents([document])
    # Extract. We provided 1 text and we pull the only embedding
    embedding = embeddings[0]
    return embedding

def shop_compute(shop_id):
    document = generate_document(shop_id) 
    embedding = generate_document_embedding(document)
    doc_version = uuid4()

    data = {
        "document": document,
        "embedding": embedding,
        "docs_version": doc_version
    }

    return db.send_docs(shop_id, marshal(data, doc_model))