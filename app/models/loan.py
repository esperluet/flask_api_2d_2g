from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"),
        nullable=False
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False
    )

    borrowed_at: Mapped[date] = mapped_column(Date, nullable=False)
    returned_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    book = relationship("Book", back_populates="loans")
    student = relationship("Student", back_populates="loans")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "book_id": self.book_id,
            "student_id": self.student_id,
            "borrowed_at": self.borrowed_at.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None
        }