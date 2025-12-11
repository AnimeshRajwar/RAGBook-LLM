from flask import Blueprint, jsonify, session
from utils.mongo_embedding_store import MongoEmbeddingStore

bp = Blueprint('user_files', __name__)

@bp.route('/user_files', methods=['GET'])
def user_files():
    user_id = session.get('user_id', 'anonymous')
    mongo_store = MongoEmbeddingStore()
    files = mongo_store.collection.distinct('doc_id', {'user_id': user_id})
    file_info = []
    import os
    uploads_folder = os.path.join(os.getcwd(), 'uploads')
    session_files = session.get('session_files', set())
    for fname in files:
        path = os.path.join(uploads_folder, fname)
        size = os.path.getsize(path) if os.path.exists(path) else None
        
        previous = fname not in session_files
        file_info.append({'name': fname, 'size': size, 'previous': previous})
    return jsonify({'files': file_info})
