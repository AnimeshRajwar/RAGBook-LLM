
import google.generativeai as genai
from typing import List
from utils.config import GEMINI_API_KEY


class EmbeddingGenerator:
    def __init__(self, model_name: str = None):
        # Always use Gemini embedding-001 model
        self.embedding_model_name = "embedding-001"
        print(f"Using Gemini API for embeddings: {self.embedding_model_name}")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.embedding_model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        print(f"Generating embeddings for {len(texts)} chunks using Gemini API...")
        embeddings = []
        for text in texts:
            try:
                # Gemini API: get embeddings for the text
                result = self.model.embed_content(content=text)
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"Error generating embedding for text: {e}")
                embeddings.append([0.0])  # fallback for error
        return embeddings