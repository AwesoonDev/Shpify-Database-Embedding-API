

from abc import ABC
from typing import List
from langchain.embeddings import OpenAIEmbeddings
from awesoon.core.models.doc import doc

from awesoon.core.shopify.documents import ShopifyObject
from langchain.text_splitter import TokenTextSplitter


class ShopifyEmbedding(ABC):
    def __init__(self, objects: List[ShopifyObject], version: str) -> None:
        self.objects = objects
        self.openai = OpenAIEmbeddings()
        self.embedding_version = version

    def get_embedded_documents(self) -> List[doc]:
        docs = self.get_documents()
        embeddings = self.openai.embed_documents(docs)
        return [
            doc(document=docs[i], embedding=embeddings[i], docs_version=self.embedding_version) for i in range(len(docs))
        ]

    def get_documents(self):
        pass


class ProductEmbedding(ShopifyEmbedding):

    def get_documents(self):
        return [object.raw() for object in self.objects]


class CategoryEmbedding(ShopifyEmbedding):

    def get_documents(self):
        docs = []
        for category in self.objects:
            docs.append(f"Here is a category of products that this store sells {category}")
        return docs


class PolicyEmbedding(ShopifyEmbedding):

    def get_documents(self):
        large_obj = ""
        for obj in self.objects:
            large_obj += obj.raw()
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=40)
        return text_splitter.split_text(large_obj)
