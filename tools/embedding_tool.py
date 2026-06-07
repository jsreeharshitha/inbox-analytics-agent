import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
import os

def generate_embedding(text: str, model_name: str = "text-embedding-004"):
    """
    Generates a 768-dimension vector embedding using Google Vertex AI.
    (Aligned with BigQuery target schema)
    """
    if not text or not text.strip():
        return [0.0] * 768

    try:
        project_id = os.getenv("PROJECT_ID", "grah-2026")
        vertexai.init(project=project_id, location="us-central1")
        model = TextEmbeddingModel.from_pretrained(model_name)
        
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_QUERY")]
        embeddings = model.get_embeddings(inputs)
        
        print(f"Generating Vertex AI query embedding using model {model_name}...")
        return embeddings[0].values
    except Exception as e:
        print(f"Vertex Embedding Error: {str(e)}")
        return [0.0] * 768
