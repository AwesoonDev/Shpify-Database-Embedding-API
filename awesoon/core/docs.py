
import re
from uuid import uuid4
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from awesoon.core.models.doc import doc
from awesoon.core.shopify.embeddings import CategoryEmbedding, PolicyEmbedding, ProductEmbedding

db = DatabaseApiClient()

def filter_by_hash(unfiltered_list, hash_map):
    filtered_list = []
    for object in unfiltered_list:
        if object.raw_hash() != hash_map.get(object.identifier()):
            filtered_list.extend(object)

    return filtered_list

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
    hashes = db.get_shop_hashes(shop_id)
    hash_map = {hash_dict.get("id"): hash_dict.get("hash") for hash_dict in hashes}

    docs = []
    dels = []
    scan_version_id = uuid4().hex

    filtered_policies = filter_by_hash(policies, hash_map)
    filtered_products = filter_by_hash(products, hash_map)
    filtered_categories = filter_by_hash(categories, hash_map)

    docs.extend(PolicyEmbedding(filtered_policies, scan_version_id).get_embedded_documents())
    docs.extend(ProductEmbedding(filtered_products, scan_version_id).get_embedded_documents())
    docs.extend(CategoryEmbedding(filtered_categories, scan_version_id).get_embedded_documents())

    return [docs, dels]


def scan_shop(shop_id, scan_id, args):
    """
    Send shop information to the database
    Args:
        shop_id: unique shop indentifier to retrieve information from
        args: includes the filter params (app_name)
    Return:
        Returns success message
    """
    app_name = args["app_name"]
    documents, deletions = generate_documents(shop_id, app_name=app_name)
    for document in documents:
        db.add_doc(scan_id, document)

    for deletion in deletions:
        db.remove_doc(scan_id, deletion)

    return True


def initiate_scan(shop_id, args):
    """
    Inform database a scan has initiated
    Args:
        shop_id: unique shop indentifier to retrieve information from
        args: includes the filter params (app_name)
    Return:
        scan id for future requests
    """
    scan_id = db.post_new_scan(shop_id)
    return scan_id
