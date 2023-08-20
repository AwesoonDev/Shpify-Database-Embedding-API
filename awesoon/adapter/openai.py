


from typing import List
from retry import retry


@retry()
def embed_texts_with_retry(texts: List[str], model_name) -> List[List[float]]:
    """Embed texts with retry

    ? Embeds texts with retry ?
    """
    
    pass

