import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL_NAME = "gemini-2.5-flash"

EMBEDDING_MODEL_NAME="embedding-001"

DOCUMENTS_DIR = "./documents"



MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'ragdb')  
if not MONGO_URI:
    raise ValueError('MONGO_URI not set in environment variables')


mongo_client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000
)
mongo_db = mongo_client[MONGO_DB_NAME]