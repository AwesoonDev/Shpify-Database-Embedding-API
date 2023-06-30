

from abc import ABC
from typing import List

import backoff
import openai
from openai.error import RateLimitError

from awesoon.core.models.doc import Doc
from awesoon.core.models.resource import ResourceInterface

EMBEDDING_MODEL = "text-embedding-ada-002"


class Embedder(ABC):

    """Embedder

    ? Creates/serves openai embeddings of documents ?

    Args:
        ABC (_type_): _description_
    """

    @classmethod
    @backoff.on_exception(backoff.expo, RateLimitError)
    def embed_resource(self, resource: ResourceInterface) -> ResourceInterface:
        docs: List[Doc] = resource.docs()
        embeddings = openai.Embedding.create(
            input=[doc.document for doc in docs], model=EMBEDDING_MODEL
        )["data"]
        for doc, emb in zip(docs, embeddings):
            doc.embedding = emb["embedding"]
        return resource

    def embed_resources(self, resources: List[ResourceInterface]) -> List[ResourceInterface]:
        docs: List[Doc] = [doc for resource in resources for doc in resource.docs()]
        embeddings = openai.Embedding.create(
            input=[doc.document for doc in docs], model=EMBEDDING_MODEL
        )["data"]
        for doc, emb in zip(docs, embeddings):
            doc.embedding = emb["embedding"]
        return resources
