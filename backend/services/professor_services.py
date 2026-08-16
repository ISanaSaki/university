from exceptions.custom_exceptions import (
    ProfessorAlreadyExistsException,
    ProfessorNotFoundException,
)
from models.professor import Professor
from schemas.professor_schema import ProfessorCreate, ProfessorUpdate
import data.storage as storage


def create_professor(data: ProfessorCreate) -> Professor:
    if data.personnel_code in storage.professors:
        raise ProfessorAlreadyExistsException(
            f"استاد با کد پرسنلی '{data.personnel_code}' قبلاً ثبت شده است."
        )
    professor = Professor(
        national_id=data.national_id,
        first_name=data.first_name,
        last_name=data.last_name,
        personnel_code=data.personnel_code,
        department=data.department,
    )
    storage.professors[professor.personnel_code] = professor
    storage.professor_counter += 1
    storage.save_all()
    return professor


def get_all_professors() -> list[Professor]:
    return list(storage.professors.values())


def get_professor_by_id(personnel_code: str) -> Professor:
    professor = storage.professors.get(personnel_code)
    if not professor:
        raise ProfessorNotFoundException(
            f"استاد با کد پرسنلی '{personnel_code}' یافت نشد."
        )
    return professor


def update_professor(personnel_code: str, data: ProfessorUpdate) -> Professor:
    professor = get_professor_by_id(personnel_code)

    if data.first_name is not None:
        professor.first_name = data.first_name.strip()
    if data.last_name is not None:
        professor.last_name = data.last_name.strip()
    if data.department is not None:
        professor.department = data.department.strip()

    new_code = data.personnel_code.strip() if data.personnel_code is not None else None
    if new_code is not None and new_code != personnel_code:
        if new_code in storage.professors:
            raise ProfessorAlreadyExistsException(
                f"استاد با کد پرسنلی '{new_code}' قبلاً ثبت شده است."
            )
        storage.professors.pop(personnel_code)
        professor.personnel_code = new_code
        storage.professors[new_code] = professor

    storage.save_all()
    return professor


def delete_professor(personnel_code: str) -> None:
    professor = get_professor_by_id(personnel_code)
    for course in list(professor.courses):
        if course.professor is professor:
            course.assign_professor(None)
        professor.remove_course(course)
    storage.professors.pop(personnel_code)
    storage.save_all()
