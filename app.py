from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, session
import logging
import os
import shutil
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from main import index_documents, query_rag
from utils.config import DOCUMENTS_DIR
from utils.auth import auth_bp
from utils.delete_file_api import bp as delete_file_bp
from utils.user_files_api import bp as user_files_bp

load_dotenv()


app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')  # Needed for session/flash
app.register_blueprint(auth_bp)
app.register_blueprint(delete_file_bp)
app.register_blueprint(user_files_bp)
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))
OUTPUTS_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'static', 'outputs'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUTS_FOLDER, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return jsonify({"status": "ok"}), 200


@app.get("/")
def index_page():
    return render_template('landing.html')


@app.get("/auth")
def auth_page():
    return render_template('auth.html')

@app.get("/app")
def app_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.auth_page'))
    return render_template('index.html')


@app.get("/start")
def start_redirect():
    return redirect(url_for('app_page'))


@app.post('/upload')
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': "No files part in request"}), 400

    files = request.files.getlist('files')
    saved = []
    try:
        for f in files:
            if f.filename == '':
                continue
            filename = secure_filename(f.filename)
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            f.save(upload_path)
            doc_dest = os.path.join(os.path.abspath(DOCUMENTS_DIR), filename)
            shutil.copy2(upload_path, doc_dest)
            saved.append(filename)

        index_documents(DOCUMENTS_DIR)

        return jsonify({'message': f'Uploaded and indexed {len(saved)} file(s)', 'files': saved}), 200
    except Exception as e:
        logging.exception('Upload failed')
        return jsonify({'error': str(e)}), 500


@app.post('/clear_storage')
def clear_storage():
    try:
        for folder in [UPLOAD_FOLDER, OUTPUTS_FOLDER]:
            for name in os.listdir(folder):
                path = os.path.join(folder, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        return jsonify({'status': 'cleared'}), 200
    except Exception as e:
        logging.exception('Failed to clear storage')
        return jsonify({'error': str(e)}), 500


@app.post('/clear_context')
def clear_context():
    try:
        for folder in [UPLOAD_FOLDER, OUTPUTS_FOLDER]:
            for name in os.listdir(folder):
                path = os.path.join(folder, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)

        # Removed chroma_db related code

        docs_abs = os.path.abspath(os.path.join(os.getcwd(), DOCUMENTS_DIR))
        if os.path.exists(docs_abs):
            for name in os.listdir(docs_abs):
                path = os.path.join(docs_abs, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)

        return jsonify({'status': 'context_cleared'}), 200
    except Exception as e:
        logging.exception('Failed to clear context')
        return jsonify({'error': str(e)}), 500


@app.post("/index")
def index_route():
    data = request.get_json(silent=True) or {}
    folder_path = data.get("folder_path") if isinstance(data, dict) else None
    if not folder_path:
        folder_path = DOCUMENTS_DIR

    try:
        logging.info(f"Indexing documents in: {folder_path}")
        result = index_documents(folder_path)
        return jsonify({"status": "success", "indexed": bool(result)}), 200
    except Exception as e:
        logging.exception("Indexing failed")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.post("/query")
def query_route():
    data = request.get_json(silent=True) or {}
    query = data.get("query") if isinstance(data, dict) else None
    if not query:
        return jsonify({"status": "error", "message": "Missing 'query' in JSON body."}), 400

    # --- Chat history tracking ---
    chat_history = session.get('chat_history', [])
    # Add the new user message to history
    chat_history.append({"role": "user", "content": query})

    try:
        logging.info(f"Received query: {query}")
        answer = query_rag(query, chat_history=chat_history)
        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": str(answer)})
        # Store back in session
        session['chat_history'] = chat_history[-20:]  # keep last 20 turns
        return jsonify({"status": "success", "query": query, "answer": str(answer)}), 200
    except Exception as e:
        logging.exception("Query failed")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.get('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.get('/preview/<path:filename>')
def preview_file(filename):
    safe = secure_filename(filename)
    out_path = os.path.join(OUTPUTS_FOLDER, safe)
    up_path = os.path.join(UPLOAD_FOLDER, safe)
    if os.path.exists(out_path):
        return redirect(url_for('static', filename=f'outputs/{safe}'))
    if os.path.exists(up_path):
        return send_from_directory(UPLOAD_FOLDER, safe)
    return jsonify({'error': 'file not found'}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

