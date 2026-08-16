from fastapi import APIRouter

from schemas.common_schema import MessageResponse
from schemas.course_schema import CourseResponse
from schemas.student_schema import StudentCreate, StudentResponse, StudentUpdate
from services import selection_services, student_services

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(body: StudentCreate):
    return student_services.create_student(body).to_dict()


@router.get("/", response_model=list[StudentResponse])
def get_all_students():
    return [student.to_dict() for student in student_services.get_all_students()]


@router.get("/{student_number}/courses", response_model=list[CourseResponse])
def get_student_courses(student_number: str):
    return [course.to_dict() for course in selection_services.get_student_courses(student_number)]


@router.get("/{student_number}", response_model=StudentResponse)
def get_student(student_number: str):
    return student_services.get_student_by_id(student_number).to_dict()


@router.put("/{student_number}", response_model=StudentResponse)
def update_student(student_number: str, body: StudentUpdate):
    return student_services.update_student(student_number, body).to_dict()


@router.delete("/{student_number}", response_model=MessageResponse)
def delete_student(student_number: str):
    student_services.delete_student(student_number)
    return {"message": "دانشجو با موفقیت حذف شد."}
