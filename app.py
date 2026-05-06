from flask import Flask, jsonify, request

from sqlalchemy import String, create_engine
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

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)