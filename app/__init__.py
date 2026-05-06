from flask import Flask, jsonify

from app.routes.books import books_bp
from app.routes.authors import authors_bp

def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(books_bp)
    app.register_blueprint(authors_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200
    
    return app