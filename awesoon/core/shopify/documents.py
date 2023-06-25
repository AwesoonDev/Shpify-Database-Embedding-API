

from abc import ABC
from awesoon.core.models.type_enums import DocType


class ShopifyObject(ABC):
    def __init__(self, raw) -> None:
        self._raw = raw
        self._raw_hash = hash(raw)
        self._identifier = self.identify()
        self._type = self.typify()

    # Set
    def process(self):
        self._processed = self.raw()

    def identify(self):
        return "unidentified"

    def typify(self):
        return "untyped"

    # Get
    def raw(self):
        return self._raw

    def raw_hash(self):
        return self._raw_hash

    def processed(self):
        return self._processed

    def identifier(self):
        return self._identifier

    def type(self):
        return self._type


class Policy(ShopifyObject):

    def typify(self):
        return DocType.policy

    def identify(self):
        return "policy"


class Product(ShopifyObject):

    def typify(self):
        return DocType.product

    def identify(self):
        return self.raw().get("id")

    def process(self):
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

    def typify(self):
        return DocType.category
    
    def identify(self):
        return self.raw()
    
    def process(self):
        category_raw = self.raw()
        processed = f"Here is a category of products that this store sells: {category_raw}"
        self._processed = processed
