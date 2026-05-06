from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.database import get_db_session
from app.models.student import Student
from app.security import require_api_key


students_bp = Blueprint("students", __name__, url_prefix="/students")


@students_bp.post("")
@require_api_key
def create_student():
    data = request.get_json(silent=True) or {}

    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    if not first_name or not last_name or not email:
        return jsonify({
            "error": "Fields 'first_name', 'last_name' and 'email' are required."
        }), 400

    with get_db_session() as session:
        existing_student = session.scalar(
            select(Student).where(Student.email == email)
        )

        if existing_student is not None:
            return jsonify({"error": "A student with this email already exists."}), 409

        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        session.add(student)
        session.commit()
        session.refresh(student)

        return jsonify(student.to_dict()), 201


@students_bp.get("")
@require_api_key
def list_students():
    with get_db_session() as session:
        statement = select(Student).order_by(Student.id.asc())
        students = session.scalars(statement).all()

        return jsonify([student.to_dict() for student in students]), 200


@students_bp.get("/<int:student_id>")
@require_api_key
def get_student(student_id: int):
    with get_db_session() as session:
        student = session.get(Student, student_id)

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(student.to_dict()), 200