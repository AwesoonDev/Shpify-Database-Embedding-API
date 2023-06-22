

from abc import ABC
from langchain.chat_models import ChatOpenAI


class ShopifyObject(ABC):
    def __init__(self, raw) -> None:
        self._raw = raw
        self.process_document()

    def process_document(self):
        self._processed = self.raw()

    def raw(self):
        return self._raw
    
    def processed(self):
        return self._processed


class Policy(ShopifyObject):
    pass


BODY_PROMPT_TEMPLATE = """Goal: The goal of this query is to extract important factual product details from marketing material for database storage. The marketing text may contain value judgements, calls to action, and stylistic flourishes. The extracted details should be summarized in a dry, formal, and succinct style, focusing on factual information. The summary should aim to use as few words as possible while including as many relevant facts as possible.
Response Length: Summarize the extracted details in a maximum of 10 sentences.
Tone: Maintain a dry, formal style that focuses on factual information.
Content Extraction: Extract as many relevant product details as possible while excluding all marketing fluff, subjective elements, and calls to action by the customer.

Marketing material:"""


class Product(ShopifyObject):

    def process_document(self):
        product_raw = self.raw()
        body_raw = product_raw.get("body_html")
        body_processed = ""
        if body_raw:
            openai = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
            body_processed = openai.predict(f"{BODY_PROMPT_TEMPLATE}{body_raw}")

        processed = f"""
Product Title: {product_raw.get("title")}
Product Type: {product_raw.get("product_type", "Undefined")}
Product URL: {product_raw.get("url")}
Brand: {product_raw.get("vendor")}
Description: {body_processed}
"""
        for variant in product_raw.get("variants"):
            processed += f"""
Variant name: {variant.get("title")}
Price: {variant.get("price", "unpriced")}
Inventory quantity: {variant.get("inventory_quantity", "Not tracked")}
Weight in grams: {variant.get("grams", "Not tracked")}
Variant URL: {variant.get("url")}
"""
        processed += f"""
Additional search tags: {product_raw.get("tags")}
"""
        self._processed = processed


class Category(ShopifyObject):
    pass
