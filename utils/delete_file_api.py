from flask import Blueprint, request, jsonify, session
import os
from utils.mongo_embedding_store import MongoEmbeddingStore
from utils.config import DOCUMENTS_DIR

bp = Blueprint('delete', __name__)

@bp.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Missing filename'}), 400
    user_id = session.get('user_id', 'anonymous')
    removed = False
    for folder in [os.path.join(os.getcwd(), 'uploads'), DOCUMENTS_DIR]:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                removed = True
            except Exception as e:
                return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500
   
    try:
        mongo_store = MongoEmbeddingStore()
        mongo_store.delete_document_embeddings(user_id, filename)
    except Exception as e:
        return jsonify({'error': f'Failed to delete embeddings: {str(e)}'}), 500
    if removed:
        return jsonify({'status': 'deleted'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404
