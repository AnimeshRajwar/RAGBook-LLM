import os
from utils.config import *  
from utils.document_processor import DocumentProcessor 
from utils.text_chunker import TextChunker 
from utils.embedding_generator import EmbeddingGenerator
from utils.rag_engine import RAGEngine 

def index_documents(folder_path: str):
    """Ingests, processes, and indexes all documents from a folder."""
    print("--- Starting Document Indexing ---")
    
    from flask import session
    from utils.mongo_embedding_store import MongoEmbeddingStore
    processor = DocumentProcessor()
    embedder = EmbeddingGenerator(EMBEDDING_MODEL_NAME)
    chunker = TextChunker(CHUNK_SIZE, CHUNK_OVERLAP, embedder)
    mongo_store = MongoEmbeddingStore()

    all_chunks = []

    user_id = session.get('user_id', 'anonymous')

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            print(f"\nProcessing {filename}...")
            document = processor.process_document(file_path)
            if document:
                chunks = chunker.create_chunks(document)
                chunk_texts = [chunk["text"] for chunk in chunks]
                embeddings = embedder.generate_embeddings(chunk_texts)
                doc_id = filename
                mongo_store.add_chunk_embeddings(user_id, doc_id, chunks, embeddings)
                all_chunks.extend(chunks)

    if not all_chunks:
        print("No documents were processed. Exiting.")
        return

    print("\n--- Document Indexing Complete ---")
    print(f"Total chunks stored in MongoDB: {len(all_chunks)}")
    return True


def query_rag(query: str):
    """Queries the RAG system to get an answer."""
    print("\n--- Querying RAG System ---")
    
   
    embedder = EmbeddingGenerator(EMBEDDING_MODEL_NAME)
    rag = RAGEngine(GEMINI_API_KEY, GEMINI_MODEL_NAME)
    from flask import session
    from utils.mongo_embedding_store import MongoEmbeddingStore
    user_id = session.get('user_id', 'anonymous')
    mongo_store = MongoEmbeddingStore()
    query_embedding = embedder.generate_embeddings([query])[0]
    
    all_chunks = mongo_store.get_user_embeddings(user_id)
    if not all_chunks:
        print("No documents in DB. Returning 'No Source Provided'.")
        return "No Source Provided"
    def cosine_similarity(a, b):
        import math
        denom_a = math.sqrt(sum(x * x for x in a))
        denom_b = math.sqrt(sum(x * x for x in b))
        if denom_a == 0 or denom_b == 0:
            return 0.0
        return sum(x * y for x, y in zip(a, b)) / (denom_a * denom_b)

    ranked = sorted(
        all_chunks,
        key=lambda chunk: cosine_similarity(query_embedding, chunk['embedding']),
        reverse=True
    )
    retrieved_chunks = [
        {"text": chunk["chunk_text"], "metadata": chunk["metadata"]}
        for chunk in ranked[:3]
    ]
    print(f"\nFound {len(retrieved_chunks)} relevant context chunks.")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"Context {i+1} (from {chunk['metadata'].get('source', '')}):")
        print(chunk['text'][:200] + "...")
        print("-" * 20)
    answer = rag.generate_response(query, retrieved_chunks)
    print("\n--- Final Answer ---")
    print(answer)
    return answer

    if __name__ == "__main__":
        if not os.path.exists(DOCUMENTS_DIR):
            os.makedirs(DOCUMENTS_DIR)
            print(f"Created directory: {DOCUMENTS_DIR}")
            print(f"Please add your PDF, DOCX, PPTX, or TXT files to the '{DOCUMENTS_DIR}' folder and run the script again.")
        else:
            index_documents(DOCUMENTS_DIR)
            while True:
                user_query = input("\nEnter your question (or type 'exit' to quit): ")
                if user_query.lower() == 'exit':
                    break
                query_rag(user_query)