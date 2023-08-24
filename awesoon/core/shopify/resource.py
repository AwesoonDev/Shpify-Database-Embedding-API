

import logging
from typing import List, Optional

from langchain.text_splitter import TokenTextSplitter

from awesoon.core.models.doc import Doc
from awesoon.core.models.doc_type_enums import DocType
from awesoon.core.resource import Resource
from awesoon.core.shopify.parsers import ProductParser


class Policy(Resource):

    def identifier(self):
        return str(self.raw().get("id"))

    def parse(self) -> "Policy":
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
        split_text = text_splitter.split_text(self.raw().get("body"))
        prepend = f"""Partial {self.raw().get("type").lower().replace("_", " ")}: """
        processed_text = [
            f"""{prepend}{text}""" for text in split_text
        ]
        self._docs = [
            Doc(
                document=text,
                hash=self.get_hash(),
                doc_identifier=self.identifier(),
                doc_type=DocType.POLICY.value
            )
            for text in processed_text
        ]
        return self


class Product(Resource):
    def __init__(self, raw, docs: Optional[List[Doc]] = None) -> None:
        super().__init__(raw, docs)
        self._parser = None

    def identifier(self):
        return str(self.raw().get("id"))

    def parse(self) -> "Product":
        self.enable_product_parser_v1()
        if self._parser:
            self._parser.parse()
            for doc in self._docs:
                doc.hash = self.get_hash()
        else:
            logging.critical("No parser was detected")
            super().parse()
        return self

    def enable_product_parser_v1(self):
        self._parser = ProductParser(self)


class Category(Resource):

    def identifier(self):
        return str(self.raw().get("id"))

    def parse(self):
        category_raw = self.raw().get("fullName")
        text = f" Here is a category of products that this store sells: {category_raw}. "
        self._docs = [
            Doc(
                document=text,
                hash=self.get_hash(),
                doc_identifier=self.identifier(),
                doc_type=DocType.CATEGORY.value
            )
        ]
        return self


class Page(Resource):

    def identifier(self):
        return str(self.raw().get("id"))

    def parse(self):
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
        split_text = text_splitter.split_text(self.raw().get("body_html"))
        prepend = f"""Partial Webpage on the online store: """
        processed_text = [
            f"""{prepend}{text}""" for text in split_text
        ]
        self._docs = [
            Doc(
                document=text,
                hash=self.get_hash(),
                doc_identifier=self.identifier(),
                doc_type=DocType.PAGE.value
            )
            for text in processed_text
        ]
        return self


