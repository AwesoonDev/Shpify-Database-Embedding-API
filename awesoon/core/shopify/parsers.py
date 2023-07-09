
from typing import List

from langchain.text_splitter import TokenTextSplitter

from awesoon.core.models.doc import Doc
from awesoon.core.models.doc_type_enums import DocType
from awesoon.core.models.resource import ResourceInterface
from awesoon.core.shopify.util import strip_tags

PRODUCT_VARIANT = """
    Variant of {product_title}.
    Name: {variant_name}.
    Price: {variant_price}.
    Inventory quantity: {inventory_quantity}.
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


def get_variant_doc_text_string(variant, product_url, product_tile):
    variant_id = variant.get("id")
    return PRODUCT_VARIANT.format(
        variant_name=variant.get("title"),
        product_title=product_tile,
        variant_price=variant.get("price"),
        inventory_quantity=variant.get("inventory_quantity"),
        weight_in_grams=variant.get("grams"),
        variant_url=f"{product_url}?variant={variant_id}"
    )


def get_product_details_string(product, product_url):
    return PRODUCT_DETAIL.format(
        product_title=product.get("title"),
        product_type=product.get("product_type"),
        product_url=product_url,
        brand=product.get("vendor"),
        search_tags=product.get("tags"),
    )


def get_product_body_string(product, body_part):
    return PRODUCT_BODY.format(
        product_title=product.get("title"),
        body_part=body_part
    )


class ProductParser:
    def __init__(self, resource: ResourceInterface) -> None:
        self.resource: ResourceInterface = resource
        self.products_url = f"{self.resource.get_shop().shop_url}/products/"
        self.parsers = [
            self.get_product_details,
            self.get_product_variants,
            self.get_product_body
        ]
        self.text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)

    def parse(self) -> ResourceInterface:
        for parser in self.parsers:
            self.resource.docs().extend(parser(self.resource.raw()))

    def get_product_details(self, product) -> List[Doc]:
        product_url = f"""{self.products_url}{product.get("handle")}"""
        result = []
        result.append(
            Doc(
                document=get_product_details_string(product, product_url),
                doc_identifier=self.resource.identifier(),
                doc_type=DocType.PRODUCT.value
            )
        )
        return result

    def get_product_variants(self, product) -> List[Doc]:
        product_url = f"""{self.products_url}{product.get("handle")}"""
        result = []
        variants = product.get("variants")
        for variant in variants:
            document_text = get_variant_doc_text_string(variant, product_url, product.get("title"))
            result.append(
                Doc(
                    document=document_text,
                    doc_identifier=self.resource.identifier(),
                    doc_type=DocType.PRODUCT.value
                )
            )
        return result

    def get_product_body(self, product) -> List[Doc]:
        split_body = self.text_splitter.split_text(
            strip_tags(product.get("body_html"))
        )
        result = []
        for body in split_body:
            result.append(
                Doc(
                    document=get_product_body_string(product, body),
                    doc_identifier=self.resource.identifier(),
                    doc_type=DocType.PRODUCT.value
                )
            )
        return result
