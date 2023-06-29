

from abc import ABC
import hashlib
from awesoon.core.models.doc_type_enums import DocType
from langchain.text_splitter import TokenTextSplitter


class ShopifyResource(ABC):
    """ShopifyResource

    Stores/serves the shopify resource in a raw format (type: Any)
    Stores/serves identity and type (implemented by children)
    Process/serve resource => A processed resource is of (type: List[str])
    Create/serve hash of resource
    
    Args:
        ABC (_type_): _description_
    """    
    def __init__(self, raw) -> None:
        self._raw = raw
        self._identifier = self.identify()
        self._type = self.typify()
        self.process()

    # Set
    def process(self):
        self._processed = [self.raw()]

    def identify(self):
        return "unidentified"

    def typify(self):
        return "untyped"

    # Get
    def raw(self):
        return self._raw

    def raw_hash(self):
        to_hash = ' '.join(self.processed())
        hash_object = hashlib.sha256()
        hash_object.update(to_hash.encode())
        hash_value = hash_object.hexdigest()
        return hash_value

    def processed(self):
        return self._processed

    def identifier(self):
        return self._identifier

    def type(self):
        return self._type


class Policy(ShopifyResource):

    def typify(self):
        return DocType.POLICY.value

    def identify(self):
        return self.raw().get("id")

    def process(self):
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
        split_text = text_splitter.split_text(self.raw().get("body"))
        prepend = f"""Partial {self.raw().get("type").lower().replace("_", " ")}: """
        processed_text = [
            f"""{prepend}{text}""" for text in split_text
        ]
        self._processed = processed_text


class ProductBody(ShopifyResource):

    def typify(self):
        return DocType.PRODUCT_BODY.value
    
    def identify(self):
        return f"""{self.raw().get("id")}_{DocType.PRODUCT_BODY.value}"""

    def process(self):
        product_raw = self.raw()
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
        split_body = text_splitter.split_text(product_raw.get("body"))
        prepend_body = f"""Partial {product_raw.get("title")} description: """
        processed_body = [f"""{prepend_body}{body_part}""" for body_part in split_body]
        self._processed = processed_body


class ProductDetail(ShopifyResource):

    def typify(self):
        return DocType.PRODUCT_DETAIL.value
    
    def identify(self):
        return self.raw().get("id")
    
    def process(self):
        product_raw = self.raw()
        processed_details = f"""Product Title: {product_raw.get("title")}. Product Type: {product_raw.get("product_type", "Undefined")}. Product URL: {product_raw.get("url")}. Brand: {product_raw.get("vendor")}. Search tags: {product_raw.get("tags")}"""
        self._processed = [processed_details]


class ProductVariant(ShopifyResource):

    def typify(self):
        return DocType.PRODUCT_VARIANT.value

    def identify(self):
        return f"""{self.raw().get("product_id")}_{self.raw().get("id")}"""

    def process(self):
        variant_raw = self.raw()
        processed_variant = f"""Variant of {variant_raw.get("product_title")}. Name: {variant_raw.get("title")}. Price: {variant_raw.get("price", "unpriced")}. Inventory quantity: {variant_raw.get("inventory_quantity", "Not tracked")}. Weight in grams: {variant_raw.get("grams", "Not tracked")}. URL: {variant_raw.get("url")}."""
        self._processed = processed_variant


class Category(ShopifyResource):

    def typify(self):
        return DocType.CATEGORY.value
    
    def identify(self):
        return self.raw().get("id")
    
    def process(self):
        category_raw = self.raw().get("fullName")
        processed = f"Here is a category of products that this store sells: {category_raw}"
        self._processed = [processed]
