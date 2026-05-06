from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id"),
        nullable=False
    )

    author = relationship("Author", back_populates="books")
    loans = relationship("Loan", back_populates="book")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author_id": self.author_id
        }