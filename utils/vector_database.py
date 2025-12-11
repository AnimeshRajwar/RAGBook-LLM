import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

class VectorDatabase:
    def __init__(self, db_path: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Connected to ChromaDB collection '{self.collection_name}' at '{db_path}'")

    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        if not chunks or not embeddings:
            print("No chunks or embeddings to add.")
            return
        ids = [chunk["id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        print(f"Added {len(chunks)} chunks to the database.")

    def query(self, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    def get_collection_count(self) -> int:
        return self.collection.count()