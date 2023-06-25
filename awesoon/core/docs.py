
from uuid import uuid4
from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from awesoon.core.shopify.documents import ShopifyObject
from awesoon.core.shopify.embeddings import CategoryEmbedding, PolicyEmbedding, ProductEmbedding

db = DatabaseApiClient()


def filter_by_hash(unfiltered_list: List[ShopifyObject], hash_map):
    update, add = []
    for object in unfiltered_list:
        hash_to_compare = hash_map.pop(object.identifier(), None)
        if hash_to_compare is None:
            add.extend(object)
        elif hash_to_compare != object.raw_rash:
            update.extend(object)

    return [update, add]


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

    update_policies, add_policies = filter_by_hash(policies, hash_map)
    update_products, add_products = filter_by_hash(products, hash_map)
    update_categories, add_categories = filter_by_hash(categories, hash_map)
    # filter_by_hash pops all ids present in the data obtained from shopify. remaining keys are marked for deletion
    del_docs = hash_map.keys()

    update_docs = []
    update_docs.extend(PolicyEmbedding(update_policies).get_embedded_documents())
    update_docs.extend(ProductEmbedding(update_products).get_embedded_documents())
    update_docs.extend(CategoryEmbedding(update_categories).get_embedded_documents())
    
    add_docs = []
    add_docs.extend(PolicyEmbedding(add_policies).get_embedded_documents())
    add_docs.extend(ProductEmbedding(add_products).get_embedded_documents())
    add_docs.extend(CategoryEmbedding(add_categories).get_embedded_documents())



    return [update_docs, add_docs, del_docs]


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
    updates, adds, deletions = generate_documents(shop_id, app_name=app_name)
    for update in updates:
        db.update_doc(scan_id, update)

    for add in adds:
        db.add_doc(scan_id, add)

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
