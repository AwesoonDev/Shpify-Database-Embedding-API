

from abc import ABC


class ShopifyObject(ABC):
    def __init__(self, raw) -> None:
        self._raw = raw

    def process_document(self):
        self._processed = self.raw()

    def raw(self):
        return self._raw
    
    def processed(self):
        return self._processed


class Policy(ShopifyObject):
    pass


class Product(ShopifyObject):

    def process_document(self):
        product_raw = self.raw()

        processed = f"""
Product Title: {product_raw.get("title")}
Product Type: {product_raw.get("product_type", "Undefined")}
Product URL: {product_raw.get("url")}
Brand: {product_raw.get("vendor")}
Description: {product_raw.get("body_html")}
"""
        for variant in product_raw.get("variants"):
            processed += f"""
Variant name: {variant.get("title")}
Price: {variant.get("price", "unpriced")}
Inventory quantity: {variant.get("inventory_quantity", "Not tracked")}
Weight in grams: {variant.get("grams", "Not tracked")}
Variant URL: {variant.get("url")}
"""
        processed += f"""
Additional search tags: {product_raw.get("tags")}
"""
        self._processed = processed


class Category(ShopifyObject):
    pass
