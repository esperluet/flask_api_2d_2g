from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.database import get_db_session
from app.models.author import Author
from app.models.book import Book
from app.security import require_api_key


books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.post("")
@require_api_key
def create_book():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    author_id = data.get("author_id")

    if not title or author_id is None:
        return jsonify({
            "error": "Both 'title' and 'author_id' are required."
        }), 400

    with get_db_session() as session:
        author = session.get(Author, author_id)

        if author is None:
            return jsonify({"error": "Author not found"}), 404

        book = Book(title=title, author_id=author_id)

        session.add(book)
        session.commit()
        session.refresh(book)

        return jsonify(book.to_dict()), 201


@books_bp.get("")
@require_api_key
def list_books():
    with get_db_session() as session:
        statement = select(Book).order_by(Book.id.asc())
        books = session.scalars(statement).all()

        return jsonify([book.to_dict() for book in books]), 200


@books_bp.get("/<int:book_id>")
@require_api_key
def get_book(book_id: int):
    with get_db_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return jsonify({"error": "Book not found"}), 404

        return jsonify(book.to_dict()), 200


@books_bp.put("/<int:book_id>")
@require_api_key
def update_book(book_id: int):
    data = request.get_json(silent=True) or {}

    with get_db_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return jsonify({"error": "Book not found"}), 404

        if "title" in data:
            title = (data.get("title") or "").strip()

            if not title:
                return jsonify({"error": "'title' cannot be empty"}), 400

            book.title = title

        if "author_id" in data:
            author = session.get(Author, data["author_id"])

            if author is None:
                return jsonify({"error": "Author not found"}), 404

            book.author_id = data["author_id"]

        session.commit()
        session.refresh(book)

        return jsonify(book.to_dict()), 200


@books_bp.delete("/<int:book_id>")
@require_api_key
def delete_book(book_id: int):
    with get_db_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return jsonify({"error": "Book not found"}), 404

        session.delete(book)
        session.commit()

        return jsonify({
            "deleted": True,
            "id": book_id
        }), 200