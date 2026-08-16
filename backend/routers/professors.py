from fastapi import APIRouter

from schemas.common_schema import MessageResponse
from schemas.course_schema import CourseResponse
from schemas.professor_schema import ProfessorCreate, ProfessorResponse, ProfessorUpdate
from services import professor_services

router = APIRouter(prefix="/professors", tags=["Professors"])


@router.post("/", response_model=ProfessorResponse, status_code=201)
def create_professor(body: ProfessorCreate):
    return professor_services.create_professor(body).to_dict()


@router.get("/", response_model=list[ProfessorResponse])
def get_all_professors():
    return [professor.to_dict() for professor in professor_services.get_all_professors()]


@router.get("/{personnel_code}/courses", response_model=list[CourseResponse])
def get_professor_courses(personnel_code: str):
    professor = professor_services.get_professor_by_id(personnel_code)
    return [course.to_dict() for course in professor.get_courses()]


@router.get("/{personnel_code}", response_model=ProfessorResponse)
def get_professor(personnel_code: str):
    return professor_services.get_professor_by_id(personnel_code).to_dict()


@router.put("/{personnel_code}", response_model=ProfessorResponse)
def update_professor(personnel_code: str, body: ProfessorUpdate):
    return professor_services.update_professor(personnel_code, body).to_dict()


@router.delete("/{personnel_code}", response_model=MessageResponse)
def delete_professor(personnel_code: str):
    professor_services.delete_professor(personnel_code)
    return {"message": "استاد با موفقیت حذف شد."}
