import voyageai
from config import settings

def generate_embedding(text: str, model: str = "voyage-3"):
    """
    Generates a vector embedding for the given text using Voyage AI.
    """
    vo = voyageai.Client(api_key=settings.VOYAGE_API_KEY)
    result = vo.embed([text], model=model, input_type="document")
    return result.embeddings[0]
