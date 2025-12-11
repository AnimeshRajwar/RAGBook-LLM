from utils.config import mongo_db
from typing import List, Dict, Any

class MongoEmbeddingStore:
    """Stores chunk embeddings and metadata in MongoDB."""

    def __init__(self, collection_name: str = "embeddings"):
        self.collection = mongo_db[collection_name]

    def delete_document_embeddings(self, user_id: str, doc_id: str):
        """
        Delete all embeddings for a specific document and user.
        """
        self.collection.delete_many({"user_id": user_id, "doc_id": doc_id})

    def add_chunk_embeddings(self, user_id: str, doc_id: str, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Stores each chunk's embedding and metadata in MongoDB.
        Each document contains: user_id, doc_id, chunk_id, chunk_text, embedding, metadata.
        """
        docs = []
        for chunk, embedding in zip(chunks, embeddings):
            doc = {
                "user_id": user_id,
                "doc_id": doc_id,
                "chunk_id": chunk["id"],
                "chunk_text": chunk["text"],
                "embedding": embedding,
                "metadata": chunk.get("metadata", {})
            }
            docs.append(doc)
        if docs:
            self.collection.insert_many(docs)

    def get_user_embeddings(self, user_id: str, doc_id: str = None):
        query = {"user_id": user_id}
        if doc_id:
            query["doc_id"] = doc_id
        return list(self.collection.find(query))

    def clear_user_embeddings(self, user_id: str):
        self.collection.delete_many({"user_id": user_id})
