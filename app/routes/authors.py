from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.database import get_db_session
from app.models.author import Author
from app.security import require_api_key


authors_bp = Blueprint("authors", __name__, url_prefix="/authors")


@authors_bp.post("")
@require_api_key
def create_author():
    data = request.get_json(silent=True) or {}

    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()

    if not first_name or not last_name:
        return jsonify({
            "error": "Both 'first_name' and 'last_name' are required."
        }), 400

    with get_db_session() as session:
        author = Author(first_name=first_name, last_name=last_name)

        session.add(author)
        session.commit()
        session.refresh(author)

        return jsonify(author.to_dict()), 201


@authors_bp.get("")
@require_api_key
def list_authors():
    with get_db_session() as session:
        statement = select(Author).order_by(Author.id.asc())
        authors = session.scalars(statement).all()

        return jsonify([author.to_dict() for author in authors]), 200


@authors_bp.get("/<int:author_id>")
@require_api_key
def get_author(author_id: int):
    with get_db_session() as session:
        author = session.get(Author, author_id)

        if author is None:
            return jsonify({"error": "Author not found"}), 404

        return jsonify(author.to_dict()), 200