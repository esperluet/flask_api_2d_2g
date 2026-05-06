from typing import List
from flask import Flask, jsonify, request

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

app = Flask(__name__)

# Database configuration

engine = create_engine(
    "postgresql+psycopg2://app:pass_word_12@db:5432/library"
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
  pass

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    def to_dict(self) -> dict :
        return {
            "id": self.id, 
            "title": self.title,
            "author": self.author
        }

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

#Create a book
@app.post("/books")
def create_book():
    data = request.get_json() or {}

    title = data.get("title").strip()
    author = data.get("author").strip()

    if not title or not author: 
        return jsonify({
            "error": "'title' and 'author' are required"
        }), 400
    
    with SessionLocal() as session:
        book = Book(title=title, author=author)

        session.add(book)
        session.commit()
        session.refresh(book)
    
    return jsonify(book.to_dict()), 201

#List books
@app.get("/books")
def list_books():
    books = None
    with SessionLocal() as session:
        statement = select(Book).order_by(Book.id.asc())

        books: List[Book] = list(session.scalars(statement).all())
    
    return jsonify([book.to_dict() for book in books]), 200

#Get book
@app.get("/books/<int:book_id>")
def get_book(book_id: int):
    book = None

    with SessionLocal() as session:
        book = session.get(Book, book_id)

    if book is None:
        return jsonify({
            "error": "Book not found"
        }), 404

    return jsonify(book.to_dict()), 200

#update book
@app.put("/books/<int:book_id>")
def update_book(book_id: int):
    data = request.get_json() or {}
    book = None

    with SessionLocal() as session:
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
@app.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    with SessionLocal() as session:
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




if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)