

from awesoon.core.db_client import DatabaseApiClient
from awesoon.core.shopify.policy import ShopifyQuey


db = DatabaseApiClient()

TEMPLATE = "The following is a friendly conversation between a customer " \
            "and an AI customer assistant. The AI is helpfull and not so much descriptive. " \
            "The AI should only talk about things relating to the products and policies. " \
            "Respond with answeres as short as possible.\n Given the shop policies:"


def get_shop_policies(shop_id):
    shop = db.get_shop(shop_id)
    return ShopifyQuey.get_shop_policies(shop["shop_url"], shop["access_token"])


def generate_shop_prompt_by_policies(policies):
    prompt = f"{TEMPLATE}\n\n"
    for i, policy in enumerate(policies, start=1):
        prompt = prompt + f"Policy {i}: {policy}"
    return prompt
