from flask import Blueprint, request, jsonify, session
import os
from utils.mongo_embedding_store import MongoEmbeddingStore
from utils.config import DOCUMENTS_DIR

bp = Blueprint('delete', __name__)

@bp.route('/delete_file', methods=['POST'])
def delete_file():
    user_id = session.get('user_id', 'anonymous')
    mongo_store = MongoEmbeddingStore()
    # Retrieve all document embeddings for the user
    user_docs = mongo_store.get_user_embeddings(user_id)
    if not user_docs:
        return jsonify({'error': 'No files found for user'}), 404

    removed = False
    errors = []
    deleted_files = []
    # Get unique doc_ids (filenames) for the user
    doc_ids = set(doc['doc_id'] for doc in user_docs if 'doc_id' in doc)
    for filename in doc_ids:
        for folder in [os.path.join(os.getcwd(), 'uploads'), DOCUMENTS_DIR]:
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    removed = True
                    deleted_files.append(filename)
                except Exception as e:
                    errors.append(f"Failed to delete file {filename}: {str(e)}")
        # Delete embeddings for this file
        try:
            mongo_store.delete_document_embeddings(user_id, filename)
        except Exception as e:
            errors.append(f"Failed to delete embeddings for {filename}: {str(e)}")

    if removed:
        return jsonify({'status': 'deleted', 'files': deleted_files, 'errors': errors}), 200
    else:
        return jsonify({'error': 'No files found or deleted', 'errors': errors}), 404
