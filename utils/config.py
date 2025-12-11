import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL_NAME = "gemini-2.5-flash"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHROMA_COLLECTION_NAME = "document_store"
CHROMA_DB_PATH = "./chroma_db"

DOCUMENTS_DIR = "./documents"

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 150

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'ragdb')  # fallback to 'ragdb' if not set
if not MONGO_URI:
    raise ValueError('MONGO_URI not set in environment variables')

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]