from exceptions.custom_exceptions import (
    StudentAlreadyExistsException,
    StudentNotFoundException,
)
from models.student import Student
from schemas.student_schema import StudentCreate, StudentUpdate
import data.storage as storage


def create_student(data: StudentCreate) -> Student:
    if data.student_number in storage.students:
        raise StudentAlreadyExistsException(
            f"دانشجو با شماره دانشجویی '{data.student_number}' قبلاً ثبت شده است."
        )
    student = Student(
        national_id=data.national_id,
        first_name=data.first_name,
        last_name=data.last_name,
        student_number=data.student_number,
        major=data.major,
    )
    storage.students[student.student_number] = student
    storage.student_counter += 1
    storage.save_all()
    return student


def get_all_students() -> list[Student]:
    return list(storage.students.values())


def get_student_by_id(student_number: str) -> Student:
    student = storage.students.get(student_number)
    if not student:
        raise StudentNotFoundException(
            f"دانشجو با شماره دانشجویی '{student_number}' یافت نشد."
        )
    return student


def update_student(student_number: str, data: StudentUpdate) -> Student:
    student = get_student_by_id(student_number)

    if data.first_name is not None:
        student.first_name = data.first_name.strip()
    if data.last_name is not None:
        student.last_name = data.last_name.strip()
    if data.major is not None:
        student.major = data.major.strip()

    new_number = data.student_number.strip() if data.student_number is not None else None
    if new_number is not None and new_number != student_number:
        if new_number in storage.students:
            raise StudentAlreadyExistsException(
                f"دانشجو با شماره دانشجویی '{new_number}' قبلاً ثبت شده است."
            )
        storage.students.pop(student_number)
        student.student_number = new_number
        storage.students[new_number] = student

    storage.save_all()
    return student


def delete_student(student_number: str) -> None:
    student = get_student_by_id(student_number)
    for course in list(student.selected_courses):
        course.remove_student(student)
    student.selected_courses.clear()
    storage.students.pop(student_number)
    storage.save_all()
