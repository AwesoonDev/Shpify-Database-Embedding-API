import html
import re
from io import StringIO
from html.parser import HTMLParser
from awesoon.core.shopify.documents import ProductBody, ProductDetail, ProductVariant


def decode_html_policies(policies):
    for policy in policies:
        policy["body"] = strip_tags(policy.get("body"))
    return policies


class MLStripper(HTMLParser):
    def __init__(self):
        """A markup language tag stripper class constructed from an html parser"""
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(html.unescape(data))

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    if not html:
        return ""
    s = MLStripper()
    s.feed(html)
    s.close()
    return re.sub('\n', '', s.get_data())

def get_id_from_gid(uri):
    match = re.search(r"/(\d+)$", uri)
    if match:
        return match.group(1)
    return "-1"


SHP_FIELDS = [
    "id", "title", "product_type", "body_html", "variants", "handle", "status", "published_at", "tags", "vendor"
]

VARIANT_FIELDS = [
    "id", "title", "grams", "inventory_quantity", "price",
]


def split_product(product, shop_url):
    """Split Product resources into details, description, and variants. 

    Args:
        product (dict): A dictionary that contains identifiers, details, a description body and variants

    Returns:
        ProductDetail
        ProductBody
        List[ProductVariant]
    """
    product = {field: product.get(field) for field in SHP_FIELDS}
    product_id = product.get("id")
    product_title = product.get("title")
    product_body = strip_tags(product.get("body_html"))
    product_url = f"""{shop_url}/products/{product.get("handle")}"""
    product_details = ProductDetail({
        "id": product_id,
        "title": product_title,
        "product_type": product.get("product_type"),
        "url": product_url,
        "vendor": product.get("vendor"),
        "tags": product.get("tags")
    })
    product_body = ProductBody({
        "id": product_id,
        "title": product_title,
        "body": product_body
    })
    product_variants = []
    variants_raw = product.get("variants")
    if variants_raw:
        variants = [{key: variant.get(key) for key in VARIANT_FIELDS} for variant in variants_raw]
        for variant in variants:
            variant_id = variant.get("id")
            variant_url = f"""{product_url}?variant={variant_id}"""
            product_variant = ProductVariant({
                "id": variant_id,
                "title": variant.get("title"),
                "product_id": product_id,
                "product_title": product_title,
                "price": variant.get("price"),
                "inventory_quantity": variant.get("inventory_quantity"),
                "grams": variant.get("grams"),
                "url": variant_url
            })
            product_variants.append(product_variant)

    return product_details, product_body, product_variants

