

from abc import ABC
from typing import List
from langchain.embeddings import OpenAIEmbeddings
from awesoon.core.models.doc import Doc

from awesoon.core.shopify.documents import ShopifyObject


class ShopifyEmbedding(ABC):
    def __init__(self, objects: List[ShopifyObject], version: str) -> None:
        self.objects = objects
        self.openai = OpenAIEmbeddings()
        self.embedding_version = version

    def get_embedded_documents(self) -> List[Doc]:
        docs = self.get_documents()
        embeddings = self.openai.embed_documents(docs)
        return [
            Doc(document=docs[i],
                embedding=embeddings[i],
                docs_version=self.embedding_version,
                type=self.objects[i].type(),
                identifier=self.objects[i].identifier(),
                hash=self.objects[i].raw_hash()
                ) for i in range(len(docs))
        ]

    def get_documents(self):
        documents = []
        for object in self.objects:
            documents.extend(object.processed())
        return documents


class ProductEmbedding(ShopifyEmbedding):
    pass


class CategoryEmbedding(ShopifyEmbedding):
    pass


class PolicyEmbedding(ShopifyEmbedding):
    pass
