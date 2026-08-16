import json
import os
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.json")
PROFESSORS_FILE = os.path.join(BASE_DIR, "professors.json")
COURSES_FILE = os.path.join(BASE_DIR, "courses.json")

students: dict = {}
professors: dict = {}
courses: dict = {}

student_counter: int = 1
professor_counter: int = 1
course_counter: int = 1


def _init_files() -> None:
    for path in (STUDENTS_FILE, PROFESSORS_FILE, COURSES_FILE):
        if not os.path.exists(path):
            _write_json({}, path)


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _write_json(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        prefix=".unireg-", suffix=".json", dir=os.path.dirname(path)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def save_all() -> None:
    _write_json({key: value.to_dict() for key, value in students.items()}, STUDENTS_FILE)
    _write_json({key: value.to_dict() for key, value in professors.items()}, PROFESSORS_FILE)
    _write_json({key: value.to_dict() for key, value in courses.items()}, COURSES_FILE)


def load_all() -> None:
    global student_counter, professor_counter, course_counter

    from models.course import Course
    from models.professor import Professor
    from models.student import Student

    _init_files()
    students.clear()
    professors.clear()
    courses.clear()

    raw_students = _read_json(STUDENTS_FILE)
    raw_professors = _read_json(PROFESSORS_FILE)
    raw_courses = _read_json(COURSES_FILE)

    student_links: dict[str, list[str]] = {}
    professor_links: dict[str, list[str]] = {}
    course_student_links: dict[str, list[str]] = {}
    course_professor_links: dict[str, str | None] = {}

    for key, data in raw_students.items():
        try:
            obj = Student(
                national_id=data["national_id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                student_number=data["student_number"],
                major=data["major"],
            )
        except (KeyError, TypeError, ValueError):
            continue
        students[obj.student_number] = obj
        student_links[obj.student_number] = list(data.get("selected_courses", []))

    for key, data in raw_professors.items():
        try:
            obj = Professor(
                national_id=data["national_id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                personnel_code=data["personnel_code"],
                department=data["department"],
            )
        except (KeyError, TypeError, ValueError):
            continue
        professors[obj.personnel_code] = obj
        professor_links[obj.personnel_code] = list(data.get("courses", []))

    for key, data in raw_courses.items():
        try:
            obj = Course(
                course_id=data["course_id"],
                title=data["title"],
                code=data["code"],
                unit=data["unit"],
                capacity=data["capacity"],
            )
        except (KeyError, TypeError, ValueError):
            continue
        courses[obj.course_id] = obj
        course_student_links[obj.course_id] = list(data.get("students", []))
        course_professor_links[obj.course_id] = data.get("professor")

    # Student <-> Course links: reconcile both stored directions and keep only valid IDs.
    for student_number, course_ids in student_links.items():
        student = students[student_number]
        for course_id in course_ids:
            course = courses.get(course_id)
            if course:
                student.select_course(course)
                course.add_student(student)

    for course_id, student_numbers in course_student_links.items():
        course = courses[course_id]
        for student_number in student_numbers:
            student = students.get(student_number)
            if student:
                course.add_student(student)
                student.select_course(course)

    # Course.professor is authoritative when present and valid.
    for course_id, personnel_code in course_professor_links.items():
        course = courses[course_id]
        professor = professors.get(personnel_code) if personnel_code else None
        if professor:
            course.assign_professor(professor)
            professor.assign_course(course)

    # Legacy professor.courses data can restore an assignment only when course has no professor.
    for personnel_code, course_ids in professor_links.items():
        professor = professors[personnel_code]
        for course_id in course_ids:
            course = courses.get(course_id)
            if course and course.professor is None:
                course.assign_professor(professor)
                professor.assign_course(course)

    student_counter = len(students) + 1
    professor_counter = len(professors) + 1
    course_counter = len(courses) + 1


def reset_storage() -> None:
    global student_counter, professor_counter, course_counter
    students.clear()
    professors.clear()
    courses.clear()
    student_counter = professor_counter = course_counter = 1
    save_all()


_init_files()
