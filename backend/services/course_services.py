from exceptions.custom_exceptions import (
    CourseAlreadyExistsException,
    CourseNotFoundException,
    InvalidCourseCapacityException,
)
from models.course import Course
from schemas.course_schema import CourseCreate, CourseUpdate
import data.storage as storage


def create_course(data: CourseCreate) -> Course:
    if data.course_id in storage.courses:
        raise CourseAlreadyExistsException(
            f"درس با شناسه '{data.course_id}' قبلاً ثبت شده است."
        )
    course = Course(
        course_id=data.course_id,
        title=data.title,
        code=data.code,
        unit=data.unit,
        capacity=data.capacity,
    )
    storage.courses[course.course_id] = course
    storage.course_counter += 1
    storage.save_all()
    return course


def get_all_courses() -> list[Course]:
    return list(storage.courses.values())


def get_course_by_id(course_id: str) -> Course:
    course = storage.courses.get(course_id)
    if not course:
        raise CourseNotFoundException(f"درس با شناسه '{course_id}' یافت نشد.")
    return course


def update_course(course_id: str, data: CourseUpdate) -> Course:
    course = get_course_by_id(course_id)
    if data.capacity is not None and data.capacity < len(course.students):
        raise InvalidCourseCapacityException(
            f"ظرفیت جدید ({data.capacity}) از تعداد دانشجویان ثبت‌نام‌شده ({len(course.students)}) کمتر است."
        )
    if data.title is not None:
        course.title = data.title.strip()
    if data.code is not None:
        course.code = data.code.strip()
    if data.unit is not None:
        course.unit = data.unit
    if data.capacity is not None:
        course.capacity = data.capacity
    storage.save_all()
    return course


def delete_course(course_id: str) -> None:
    course = get_course_by_id(course_id)
    for student in list(course.students):
        student.drop_course(course)
        course.remove_student(student)
    if course.professor is not None:
        course.professor.remove_course(course)
        course.assign_professor(None)
    storage.courses.pop(course_id)
    storage.save_all()
