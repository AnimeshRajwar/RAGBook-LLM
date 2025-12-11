from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingGenerator:
    """Generates embeddings for text chunks using a Sentence-Transformer model."""

    def __init__(self, model_name: str):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded.")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()