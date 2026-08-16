from exceptions.custom_exceptions import (
    CourseAlreadySelectedException,
    CourseFullException,
    CourseNotFoundException,
    CourseNotSelectedException,
    ProfessorNotFoundException,
    StudentNotFoundException,
)
import data.storage as storage


def select_course_for_student(student_number: str, course_id: str) -> dict:
    student = storage.students.get(student_number)
    if not student:
        raise StudentNotFoundException(
            f"دانشجو با شماره دانشجویی '{student_number}' یافت نشد."
        )
    course = storage.courses.get(course_id)
    if not course:
        raise CourseNotFoundException(f"درس با شناسه '{course_id}' یافت نشد.")
    if course in student.selected_courses:
        raise CourseAlreadySelectedException(
            f"دانشجو قبلاً درس '{course.title}' را انتخاب کرده است."
        )
    if course.is_full():
        raise CourseFullException(f"ظرفیت درس '{course.title}' تکمیل شده است.")
    student.select_course(course)
    course.add_student(student)
    storage.save_all()
    return {"message": f"درس '{course.title}' با موفقیت برای دانشجو انتخاب شد."}


def drop_course_for_student(student_number: str, course_id: str) -> dict:
    student = storage.students.get(student_number)
    if not student:
        raise StudentNotFoundException(
            f"دانشجو با شماره دانشجویی '{student_number}' یافت نشد."
        )
    course = storage.courses.get(course_id)
    if not course:
        raise CourseNotFoundException(f"درس با شناسه '{course_id}' یافت نشد.")
    if course not in student.selected_courses:
        raise CourseNotSelectedException(
            f"دانشجو درس '{course.title}' را انتخاب نکرده است."
        )
    student.drop_course(course)
    course.remove_student(student)
    storage.save_all()
    return {"message": f"درس '{course.title}' با موفقیت حذف شد."}


def get_student_courses(student_number: str) -> list:
    student = storage.students.get(student_number)
    if not student:
        raise StudentNotFoundException(
            f"دانشجو با شماره دانشجویی '{student_number}' یافت نشد."
        )
    return student.get_courses()


def assign_professor_to_course(personnel_code: str, course_id: str) -> dict:
    professor = storage.professors.get(personnel_code)
    if not professor:
        raise ProfessorNotFoundException(
            f"استاد با کد پرسنلی '{personnel_code}' یافت نشد."
        )
    course = storage.courses.get(course_id)
    if not course:
        raise CourseNotFoundException(f"درس با شناسه '{course_id}' یافت نشد.")

    old_professor = course.professor
    if old_professor is professor:
        return {"message": f"درس '{course.title}' از قبل به استاد '{professor.get_full_name()}' تخصیص داده شده است."}
    if old_professor is not None:
        old_professor.remove_course(course)

    course.assign_professor(professor)
    professor.assign_course(course)
    storage.save_all()
    return {"message": f"درس '{course.title}' با موفقیت به استاد '{professor.get_full_name()}' تخصیص داده شد."}
