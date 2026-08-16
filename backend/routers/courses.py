from fastapi import APIRouter

from schemas.common_schema import MessageResponse
from schemas.course_schema import CourseCreate, CourseResponse, CourseUpdate
from schemas.student_schema import StudentResponse
from services import course_services

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse, status_code=201)
def create_course(body: CourseCreate):
    return course_services.create_course(body).to_dict()


@router.get("/", response_model=list[CourseResponse])
def get_all_courses():
    return [course.to_dict() for course in course_services.get_all_courses()]


@router.get("/{course_id}/students", response_model=list[StudentResponse])
def get_course_students(course_id: str):
    course = course_services.get_course_by_id(course_id)
    return [student.to_dict() for student in course.students]


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str):
    return course_services.get_course_by_id(course_id).to_dict()


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: str, body: CourseUpdate):
    return course_services.update_course(course_id, body).to_dict()


@router.delete("/{course_id}", response_model=MessageResponse)
def delete_course(course_id: str):
    course_services.delete_course(course_id)
    return {"message": "درس با موفقیت حذف شد."}
