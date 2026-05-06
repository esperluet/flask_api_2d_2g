from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.database import get_db_session
from app.models.book import Book
from app.models.loan import Loan
from app.models.student import Student
from app.security import require_api_key


loans_bp = Blueprint("loans", __name__, url_prefix="/loans")


@loans_bp.post("")
@require_api_key
def create_loan():
    data = request.get_json(silent=True) or {}

    book_id = data.get("book_id")
    student_id = data.get("student_id")

    if book_id is None or student_id is None:
        return jsonify({
            "error": "Both 'book_id' and 'student_id' are required."
        }), 400

    with get_db_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return jsonify({"error": "Book not found"}), 404

        student = session.get(Student, student_id)

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        active_loan = session.scalar(
            select(Loan).where(
                Loan.book_id == book_id,
                Loan.returned_at.is_(None)
            )
        )

        if active_loan is not None:
            return jsonify({
                "error": "This book is already borrowed."
            }), 409

        loan = Loan(
            book_id=book_id,
            student_id=student_id,
            borrowed_at=date.today(),
            returned_at=None
        )

        session.add(loan)
        session.commit()
        session.refresh(loan)

        return jsonify(loan.to_dict()), 201


@loans_bp.get("")
@require_api_key
def list_loans():
    with get_db_session() as session:
        statement = select(Loan).order_by(Loan.id.asc())
        loans = session.scalars(statement).all()

        return jsonify([loan.to_dict() for loan in loans]), 200


@loans_bp.get("/active")
@require_api_key
def list_active_loans():
    with get_db_session() as session:
        statement = (
            select(Loan)
            .where(Loan.returned_at.is_(None))
            .order_by(Loan.id.asc())
        )

        loans = session.scalars(statement).all()

        return jsonify([loan.to_dict() for loan in loans]), 200


@loans_bp.put("/<int:loan_id>/return")
@require_api_key
def return_book(loan_id: int):
    with get_db_session() as session:
        loan = session.get(Loan, loan_id)

        if loan is None:
            return jsonify({"error": "Loan not found"}), 404

        if loan.returned_at is not None:
            return jsonify({
                "error": "This loan is already closed."
            }), 409

        loan.returned_at = date.today()

        session.commit()
        session.refresh(loan)

        return jsonify(loan.to_dict()), 200