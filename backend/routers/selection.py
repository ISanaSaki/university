from fastapi import APIRouter

from schemas.common_schema import MessageResponse
from schemas.course_schema import CourseResponse
from services import selection_services

router = APIRouter(prefix="/selection", tags=["Selection"])


@router.post("/select", response_model=MessageResponse)
def select_course(student_number: str, course_id: str):
    return selection_services.select_course_for_student(student_number, course_id)


@router.delete("/drop", response_model=MessageResponse)
def drop_course(student_number: str, course_id: str):
    return selection_services.drop_course_for_student(student_number, course_id)


@router.get("/student/{student_number}/courses", response_model=list[CourseResponse])
def get_student_courses(student_number: str):
    return [course.to_dict() for course in selection_services.get_student_courses(student_number)]


@router.post("/assign-professor", response_model=MessageResponse)
def assign_professor(personnel_code: str, course_id: str):
    return selection_services.assign_professor_to_course(personnel_code, course_id)
