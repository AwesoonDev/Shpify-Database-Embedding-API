
from uuid import uuid4
from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from awesoon.core.models.scan import ScanStatus
from awesoon.core.shopify.documents import ShopifyObject
from awesoon.core.shopify.embeddings import ShopifyEmbedding
import logging

db = DatabaseApiClient()


def filter_by_hash(shopify_raw: List[ShopifyObject], hash_map):
    """
    Filter the list of ShopifyObject into objects to update, add, delete, and ignore.
    Args:
        shopify_raw: A list of ShopifyObject to filter as returned by generate_raw_documents
        hash_map: a dict of ids and hashes as returned by fetch_hash_map
    Return:
        update_raw: 
        update_ids:
        add_raw:
        del_ids:
    """
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

    # this function pops all ids present in the data obtained from shopify.
    # remaining ids are marked for deletion. value[1] is the doc_id.
    del_ids = [value[1] for value in hash_map.values()]
    return update_raw, update_ids, add_raw, del_ids


def fetch_hash_map(scan_id):
    """
    Fetch document hashes and ids and restructure into a hash map
    Args:
        scan_id: unique scan identifier that holds the desired docs
    Return:
        Dictionary of {local document identifier: [hash, document's unique database id]}
    """
    hashes = db.get_shop_docs(scan_id)
    hash_map = {hash_dict.get("doc_identifier"): [hash_dict.get("hash"), hash_dict.get("id")] for hash_dict in hashes}
    return hash_map


def generate_raw_documents(shop_id, app_name):
    """
    generate documents for a shop
    Args:
        shop_id: unique shop indentifier to retrieve information from
    Return:
        list of raw shopify objects
    """
    shop = db.get_shop_installation(shop_id, app_name)
    platform = "shopify"
    url = shop["shop_url"]
    token = shop["access_token"]
    shopify_raw = []
    shopify_raw.extend(queries[platform].get_shop_policies(url, token))
    shopify_raw.extend(queries[platform].get_shop_products(url, token))
    shopify_raw.extend(queries[platform].get_shop_categories(url, token))
    return shopify_raw


def send_docs(scan_id, update_ids_docs, add_docs, del_ids):
    """
    Sends all of the docs that we have generated
    """
    for id_doc in update_ids_docs:
        db.update_doc(id_doc[0], id_doc[1])

    for doc in add_docs:
        db.add_doc(scan_id, doc)

    for id in del_ids:
        db.remove_doc(id)

    return True


def scan_shop(shop_id, scan_id, args):
    """
    Send shop information to the database
    Args:
        shop_id: unique shop indentifier to retrieve information from
        args: includes the filter params (app_name)
    Return:
        Returns success message
    """
    db.update_scan(scan_id, ScanStatus.IN_PROGRESS)
    app_name = args["app_name"]
    try:
        shopify_raw = generate_raw_documents(shop_id, app_name=app_name)
        hash_map = fetch_hash_map(scan_id)
        update_raw, update_ids, add_raw, del_ids = filter_by_hash(shopify_raw, hash_map)
        update_ids_docs = zip(update_ids, ShopifyEmbedding(update_raw).get_embedded_documents())
        add_docs = ShopifyEmbedding(add_raw).get_embedded_documents()
        status = send_docs(scan_id, update_ids_docs, add_docs, del_ids)
        
        if status:
            db.update_scan(scan_id, ScanStatus.COMPLETED)
            return True
        
    except Exception:
        logging.exception("Scan error happened")
        db.update_scan(scan_id, ScanStatus.ERROR)
        return False


def initiate_scan(new_scan):
    """
    Initiate a new scan in the database
    Args:
        new_scan: A scan object
    Return:
        scan id for future requests, status for response code
    """
    return db.post_new_scan(new_scan)

