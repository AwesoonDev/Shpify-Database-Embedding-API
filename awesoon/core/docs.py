
from uuid import uuid4
from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from awesoon.core.models.scan import scan_status, ScanStatus
from awesoon.core.shopify.documents import ShopifyObject
from awesoon.core.shopify.embeddings import ShopifyEmbedding
# CategoryEmbedding, PolicyEmbedding, ProductEmbedding

db = DatabaseApiClient()


def filter_by_hash(shopify_raw: List[ShopifyObject], hash_map):
    update_raw, update_ids, add_raw = []
    for object in shopify_raw:
        hash_to_compare = hash_map.pop(object.identifier(), None)
        if hash_to_compare is None:
            add_raw.append(object)
        # hash_to_compare[0] is the hash
        elif hash_to_compare[0] != object.raw_rash:
            # hash_to_compare[1] is the doc_id needed to update
            update_raw.append(object)
            update_ids.append(hash_to_compare[1])

    return update_raw, update_ids, add_raw


def generate_documents(shop_id, scan_id, app_name):
    """
    generate documents for a shop
    Args:
        shop_id: unique shop indentifier to retrieve information from
    Return:
        list of documents
    """
    shop = db.get_shop_installation(shop_id, app_name=app_name)
    platform = "shopify"
    url = shop["shop_url"]
    token = shop["access_token"]
    policies = queries[platform].get_shop_policies(url, token)
    products = queries[platform].get_shop_products(url, token)
    categories = queries[platform].get_shop_categories(url, token)

    hashes = db.get_shop_docs(scan_id)
    hash_map = {hash_dict.get("doc_identifier"): [hash_dict.get("hash"), hash_dict.get("id")] for hash_dict in hashes}

    shopify_raw = policies + products + categories
    update_raw, update_ids, add_raw = filter_by_hash(shopify_raw, hash_map)
    # filter_by_hash pops all ids present in the data obtained from shopify.
    # remaining ids are marked for deletion. value[1] is the doc_id.
    del_ids = [value[1] for value in hash_map.values()]

    update_docs = ShopifyEmbedding(update_raw).get_embedded_documents()
    add_docs = ShopifyEmbedding(add_raw).get_embedded_documents()

    return update_docs, update_ids, add_docs, del_ids


def scan_shop(shop_id, scan_id, args):
    """
    Send shop information to the database
    Args:
        shop_id: unique shop indentifier to retrieve information from
        args: includes the filter params (app_name)
    Return:
        Returns success message
    """
    db.update_scan(scan_id, scan_status(ScanStatus.IN_PROGRESS))
    app_name = args["app_name"]
    try:
        update_docs, update_ids, add_docs, del_ids = generate_documents(shop_id, app_name=app_name)
        for i in range(update_docs):
            db.update_doc(update_ids[i], update_docs[i])

        for doc in add_docs:
            db.add_doc(scan_id, doc)

        for id in del_ids:
            db.remove_doc(id)

        db.update_scan(scan_id, scan_status(ScanStatus.COMPLETED))
        return True
    except Exception:
        db.update_scan(scan_id, scan_status(ScanStatus.ERROR))
        return False


def initiate_scan(new_scan):
    """
    Inform database a scan has initiated
    Args:
        shop_id: unique shop indentifier to retrieve information from
        args: includes the filter params (app_name)
    Return:
        scan id for future requests, status for response code
    """
    return db.post_new_scan(new_scan)

