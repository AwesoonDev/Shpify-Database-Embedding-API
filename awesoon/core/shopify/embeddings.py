

from abc import ABC
from typing import List
from langchain.embeddings import OpenAIEmbeddings
from awesoon.core.models.doc import Doc

from awesoon.core.shopify.documents import ShopifyResource


class ShopifyEmbedding(ABC):
    """ShopifyEmbedding

    ? Creates/serves openai embeddings of documents ?

    Args:
        ABC (_type_): _description_
    """    
    def __init__(self, objects: List[ShopifyResource]) -> None:
        self.objects = objects
        self.openai = OpenAIEmbeddings()

    def get_embedded_documents(self) -> List[Doc]:
        docs = self.get_documents()
        embeddings = self.openai.embed_documents([doc.get("document") for doc in docs])
        # doc_embeddings = zip(docs, embeddings)
        return [
            Doc(document=doc["document"],
                embedding=emb,
                doc_type=doc["type"],
                doc_identifier=doc["identifier"],
                hash=doc["hash"]
                ) for doc, emb in zip(docs, embeddings)
        ]

    def get_documents(self):
        docs = []
        for object in self.objects:
            for doc in object.processed():
                docs.append({
                        "document": doc,
                        "type": object.type(),
                        "identifier": object.identifier(),
                        "hash": object.raw_hash()
                    })
        return docs


class ProductEmbedding(ShopifyEmbedding):
    pass


class CategoryEmbedding(ShopifyEmbedding):
    pass


class PolicyEmbedding(ShopifyEmbedding):
    pass
