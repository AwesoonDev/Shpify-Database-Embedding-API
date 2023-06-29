
from typing import List
from awesoon.core.models.doc import Doc
from awesoon.core.shopify.resource import Product
from langchain.text_splitter import TokenTextSplitter


PRODUCT_VARIANT = """
    Variant of {product_title}.
    Name: {variant_name}.
    Price: {variant_price}.
    Inventory quantity: {quantity}.
    Weight in grams: {weight_in_grams}.
    URL: {variant_url}.
"""

PRODUCT_DETAIL = """
Product Title: {product_title}.
Product Type: {product_type}.
Product URL: {product_url}.
Brand: {brand}.
Search tags: {search_tags}
"""

PRODUCT_BODY = """
Partial {product_title} description: {body_part}
"""


def get_variant_doc_text(variant, product_url):
    variant_id = variant.get("id")
    return PRODUCT_VARIANT.format(
        product_id=variant.get("id"),
        title=variant.get("title"),
        product_id=variant.get("title"),
        product_title=variant.get("title"),
        price=variant.get("price"),
        inventory_quantity=variant.get("inventory_quantity"),
        grams=variant.get("grams"),
        url=f"{product_url}?variant={variant_id}"
    )


def get_product_details(product, product_url):
    return PRODUCT_DETAIL.format(
        product_title=product.get("title"),
        product_type=product.get("product_type"),
        product_url=product_url,
        brand=product.get("vendor"),
        search_tags=product.get("tags"),
    )


def get_product_body(product, body_part):
    return PRODUCT_BODY.format(
        product_title=product.get("title"),
        body_part=body_part
    )


class ProductParser:
    def __init__(self, resource: Product) -> None:
        self.resource = resource
        self.parsers = [
            self.get_product_details,
            self.get_product_variants,
            self.get_product_body
        ]
        self.text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)

    def parse(self) -> Product:
        for parser in self.parsers:
            self.resource.docs().extend(parser(self, self.resource.raw()))

    def get_product_details(self, product) -> List[Doc]:
        product_url = f"""{self.resource.get_shop().shop_url}/products/{product.get("handle")}"""
        result = []
        result.append(
            Doc(
                document=get_product_details(product, product_url),
                doc_identifier=f"""{product.get("id")}"""
            )
        )
        return result

    def get_product_variants(self, product) -> List[Doc]:
        product_url = f"""{self.resource.get_shop().shop_url}/products/{product.get("handle")}"""
        result = []
        variants = product.get("variants")
        for variant in variants:
            document_text = get_variant_doc_text(variant, product_url)
            result.append(
                Doc(
                    document=document_text,
                    doc_identifier=f"""{product.get("id")}_{variant.get("id")}"""
                )
            )
        return result

    def get_product_body(self, product) -> List[Doc]:
        split_body = self.text_splitter.split_text(product.get("body"))
        result = []
        for body in split_body:
            result.append(
                Doc(
                    document=get_product_body(product, body),
                    doc_identifier=f"""{product.get("id")}_product_body"""
                )
            )
        return result
