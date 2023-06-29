


from abc import ABC
from typing import List
import openai
from awesoon.core.models.doc import Doc
from awesoon.core.resource import Resource

EMBEDDING_MODEL = "text-davinci-002"


class Embedder(ABC):

    """Embedder

    ? Creates/serves openai embeddings of documents ?

    Args:
        ABC (_type_): _description_
    """

    @classmethod
    def embed_resource(self, resource: Resource) -> Resource:
        docs: List[Doc] = resource.docs()
        embeddings = openai.Embedding.create(
            input=[doc.document for doc in docs], model=EMBEDDING_MODEL
        )
        for doc, emb in zip(docs, embeddings):
            doc.embedding = emb
        resource.set_docs(docs)
        return resource
