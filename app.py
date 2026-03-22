"""
app.py  –  Flask API for the AI Tutor
"""
import os, json, traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import config
from ingest import ingest_pdf
from retrieval import retrieve
from generation import generate_answer

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024   # 100 MB limit


@app.route("/")
def index():
    return send_file("index.html")


# ---------- helpers -----------------------------------------------------------

def allowed_file(filename):
    return filename.lower().endswith(".pdf")


def list_books():
    if not os.path.isdir(config.INDEX_FOLDER):
        return []
    return [d for d in os.listdir(config.INDEX_FOLDER)
            if os.path.isdir(os.path.join(config.INDEX_FOLDER, d))]


# ---------- endpoints ---------------------------------------------------------

@app.route("/api/books", methods=["GET"])
def get_books():
    """List all ingested books."""
    try:
        return jsonify({"books": list_books()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/books/<book_name>", methods=["DELETE"])
def delete_book(book_name):
    """Delete a book's index so a new one can be uploaded."""
    try:
        import shutil, stat
        store_dir = os.path.join(config.INDEX_FOLDER, book_name)
        if not os.path.isdir(store_dir):
            return jsonify({"error": "Book not found"}), 404

        # Windows fix: remove read-only flag before deleting
        def force_remove(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(store_dir, onerror=force_remove)

        # also remove the uploaded PDF if it exists
        for f in os.listdir(config.UPLOAD_FOLDER):
            if os.path.splitext(f)[0] == book_name:
                os.remove(os.path.join(config.UPLOAD_FOLDER, f))
        return jsonify({"success": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload():
    """Upload + ingest a PDF textbook."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are supported"}), 400

        filename  = secure_filename(file.filename)
        book_name = os.path.splitext(filename)[0]
        save_path = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(save_path)

        summary = ingest_pdf(save_path, book_name)
        return jsonify({"success": True, "summary": summary})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/ask", methods=["POST"])
def ask():
    """Answer a student question using context pruning."""
    try:
        data = request.get_json(force=True)
        query     = (data.get("query") or "").strip()
        book_name = (data.get("book_name") or "").strip()

        if not query:
            return jsonify({"error": "query is required"}), 400
        if not book_name:
            return jsonify({"error": "book_name is required"}), 400
        if book_name not in list_books():
            return jsonify({"error": f"Book '{book_name}' not found. Upload it first."}), 404

        if not config.GEMINI_API_KEY:
            return jsonify({"error": "GEMINI_API_KEY not set in .env"}), 500

        # --- Context Pruning happens here ---
        selected_chunks, pruning_stats = retrieve(query, book_name)

        # --- Generate answer ---
        result = generate_answer(query, selected_chunks)

        return jsonify({
            "answer":           result["answer"],
            "prompt_tokens":    result["prompt_tokens"],
            "completion_tokens":result["completion_tokens"],
            "cost_usd":         result["cost_usd"],
            "pruning_stats":    pruning_stats
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ---------- run ---------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  AI Tutor – Context Pruning Edition")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("=" * 55)
    app.run(debug=True, port=5000)
