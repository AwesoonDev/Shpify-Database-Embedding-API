

from abc import ABC
from typing import List
import openai
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
    def embed_resource(self, resource: ResourceInterface) -> ResourceInterface:
        docs: List[Doc] = resource.docs()
        embeddings = openai.Embedding.create(
            input=[doc.document for doc in docs], model=EMBEDDING_MODEL
        )["data"]
        for doc, emb in zip(docs, embeddings):
            doc.embedding = emb["embedding"]
        resource.set_docs(docs)
        return resource
