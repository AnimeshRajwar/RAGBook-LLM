import google.generativeai as genai
from typing import List, Dict

class RAGEngine:
    """Retrieval-Augmented Generation engine using Gemini."""

    def __init__(self, api_key: str, model_name: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        print(f"RAG Engine initialized with Gemini model: {model_name}")

    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generates a response from Gemini based on the query and context."""
        if not context_chunks:
            return "Sorry, I couldn't find any relevant information in the provided documents to answer your question."

        context = "\n\n---\n\n".join([chunk['text'] for chunk in context_chunks])
        
        prompt = f"""
        You are a helpful assistant. Answer the user's question based only on the context provided below.
        If the context does not contain the answer, state that you don't have enough information.
        Be concise and accurate.

        CONTEXT:
        {context}

        QUESTION:
        {query}

        ANSWER:
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred while generating the response: {e}"