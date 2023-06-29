

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


class Product(ShopifyResource):

    def typify(self):
        return DocType.PRODUCT.value

    def identify(self):
        return self.raw().get("id")

    def process(self):
        product_raw = self.raw()
        product_title = product_raw.get("title")

        # Process the common product details
        processed_details = f"""Product Title: {product_title}. Product Type: {product_raw.get("product_type", "Undefined")}. Product URL: {product_raw.get("url")}. Brand: {product_raw.get("vendor")}. Search tags: {product_raw.get("tags")}"""

        # Process the product description
        processed_desc = f"""Description: {product_raw.get("body_html")}"""

        # Process product variants
        processed_variants = []
        for variant in product_raw.get("variants"):
            processed_variants.append(f"""Variant of {product_title}. Name: {variant.get("title")}. Price: {variant.get("price", "unpriced")}. Inventory quantity: {variant.get("inventory_quantity", "Not tracked")}. Weight in grams: {variant.get("grams", "Not tracked")}. URL: {variant.get("url")}.""")

        # Process the specification
        # processed_specs = f"""Product Title: {product_title}. Product Type: {product_raw.get("product_type", "Undefined")}. Product URL: {product_raw.get("url")}. Brand: {product_raw.get("vendor")}. """
        # for variant in product_raw.get("variants"):
        #     processed_specs += f"""Variant name: {variant.get("title")}. Price: {variant.get("price", "unpriced")}. Inventory quantity: {variant.get("inventory_quantity", "Not tracked")}. Weight in grams: {variant.get("grams", "Not tracked")}. Variant URL: {variant.get("url")}. """
        # processed_specs += f"""Additional search tags: {product_raw.get("tags")}"""

        # # Process the decription
        # processed_desc = f"""desc: {product_raw.get("body_html")}"""

        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
        split_text = text_splitter.split_text(processed_desc)
        prepend_text = f"""Partial {product_title} description: """
        processed_text = []
        # details is a single string
        processed_text.append(processed_details)
        # split_text is a list of strings
        processed_text.extend([f"""{prepend_text}{text}""" for text in split_text])
        # variants is a list of strings
        processed_text.extend(processed_variants)
        
        self._processed = processed_text


class Category(ShopifyResource):

    def typify(self):
        return DocType.CATEGORY.value
    
    def identify(self):
        return self.raw().get("id")
    
    def process(self):
        category_raw = self.raw().get("fullName")
        processed = f"Here is a category of products that this store sells: {category_raw}"
        self._processed = [processed]
