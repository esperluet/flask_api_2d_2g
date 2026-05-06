from typing import List

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.database import get_db_session
from app.models.book import Book

books_bp = Blueprint("books", __name__)

#Create a book
@books_bp.post("/books")
def create_book():
    data = request.get_json() or {}

    title = data.get("title").strip()
    author = data.get("author").strip()

    if not title or not author: 
        return jsonify({
            "error": "'title' and 'author' are required"
        }), 400
    
    with get_db_session() as session:
        book = Book(title=title, author=author)

        session.add(book)
        session.commit()
        session.refresh(book)
    
    return jsonify(book.to_dict()), 201

#List books
@books_bp.get("/books")
def list_books():
    books = None
    with get_db_session() as session:
        statement = select(Book).order_by(Book.id.asc())

        books: List[Book] = list(session.scalars(statement).all())
    
    return jsonify([book.to_dict() for book in books]), 200

#Get book
@books_bp.get("/books/<int:book_id>")
def get_book(book_id: int):
    book = None

    with get_db_session() as session:
        book = session.get(Book, book_id)

    if book is None:
        return jsonify({
            "error": "Book not found"
        }), 404

    return jsonify(book.to_dict()), 200

#update book
@books_bp.put("/books/<int:book_id>")
def update_book(book_id: int):
    data = request.get_json() or {}
    book = None

    with get_db_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404
        
        if "title" in data:
            title = data.get("title").strip()

            if not title:
                return jsonify({"error": "title can not be empty"}), 400
            book.title = title
        
        if "author" in data:
            author = data.get("author").strip()

            if not author:
                return jsonify({"error": "author can not be empty"}), 400
            book.author = author
        
        session.commit()
        session.refresh(book)
    return jsonify(book.to_dict()), 200

#Delete a book
@books_bp.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    with get_db_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404
        
        session.delete(book)
        session.commit()

        return jsonify({
                "deleted": True,
                "id": book_id
            }), 200
