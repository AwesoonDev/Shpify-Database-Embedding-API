
from uuid import uuid4
from typing import List
from awesoon.core.db_client import DatabaseApiClient
from awesoon.core import queries
from awesoon.core.models.doc_type_enums import DocType
from awesoon.core.models.scan import ScanStatus
from awesoon.core.shopify.documents import ShopifyResource
from awesoon.core.shopify.embeddings import ShopifyEmbedding
import logging

db = DatabaseApiClient()


def filter_by_hash(shopify_raw: List[ShopifyResource], hash_map, guid_map):
    """
    Filter the list of ShopifyObject into objects to update, add, delete, and ignore.
    Args:
        shopify_raw: A list of ShopifyObject to filter as returned by generate_raw_documents
        hash_map: a dict of ids: [hash, type] as returned by fetch_hash_map
    Return:
        update_raw: 
        update_ids:
        add_raw:
        del_ids:
    """
    update_raw, update_ids, add_raw, del_ids = [], [], [], []
    for object in shopify_raw:
        obj_id = str(object.identifier())
        doc_hash, doc_type, db_id = hash_map.pop(obj_id, (None, None, None))
        if doc_hash is None:
            add_raw.append(object)
        elif doc_hash != object.raw_hash():
            # If the underlying is a product then we update (could be just eg inventory changes).
            # Otherwise add/remove (categories and policies must be completely removed and added)
            if doc_type == DocType.PRODUCT.value:
                update_raw.append(object)
                update_ids.append(db_id)
            else:
                add_raw.append(object)
                del_ids.extend(guid_map.get(obj_id))

    # this function pops all ids present in the data obtained from shopify.
    # remaining ids are marked for deletion.
    remaining_keys = hash_map.keys()
    for key in remaining_keys:
        del_ids.extend(guid_map.get(key))
    return update_raw, update_ids, add_raw, del_ids


def fetch_hash_map(shop_id):
    """
    Fetch document hashes and ids and restructure into a hash map
    Args:
        scan_id: unique scan identifier that holds the desired docs
    Return:
        Dictionary of {local document identifier: [hash, document's unique database id]}
    """
    hashes = db.get_shop_docs(shop_id)
    hash_map = {}
    guid_map = {}
    for hash_dict in hashes:
        doc_id = hash_dict.get("doc_identifier")
        doc_hash = hash_dict.get("hash")
        doc_type = hash_dict.get("doc_type")
        db_id = hash_dict.get("id")
        hash_map[doc_id] = [doc_hash, doc_type, db_id]
        if guid_map.get(doc_id):
            guid_map[doc_id].append(db_id)
        else:
            guid_map[doc_id] = [db_id]
    return hash_map, guid_map


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
        hash_map, guid_map = fetch_hash_map(shop_id)
        update_raw, update_ids, add_raw, del_ids = filter_by_hash(shopify_raw, hash_map, guid_map)
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

