
import re
from uuid import uuid4
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from awesoon.core.models.doc import doc
from awesoon.core.shopify.embeddings import CategoryEmbedding, PolicyEmbedding, ProductEmbedding

db = DatabaseApiClient()


def generate_documents(shop_id, app_name):
    """
    generate documents for a shop
    Args:
        shop_id: unique shop indentifier to retrieve information from
    Return:
        list of documents
    """
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    policies = queries["shopify"].get_shop_policies(shop["shop_url"], shop["access_token"])
    products = queries["shopify"].get_shop_products(shop["shop_url"], shop["access_token"])
    categories = queries["shopify"].get_shop_categories(shop["shop_url"], shop["access_token"])
    scan_version_id = uuid4().hex
    docs = []
    docs.extend(PolicyEmbedding(policies, scan_version_id).get_embedded_documents())
    docs.extend(ProductEmbedding(products, scan_version_id).get_embedded_documents())
    docs.extend(CategoryEmbedding(categories, scan_version_id).get_embedded_documents())

    return docs


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
    documents = generate_documents(shop_id, app_name=app_name)
    for document in documents:
        db.add_doc(shop_id, document)

    return True
