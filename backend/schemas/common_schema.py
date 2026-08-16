from pydantic import BaseModel

from schemas.course_schema import CourseResponse
from schemas.professor_schema import ProfessorResponse
from schemas.student_schema import StudentResponse


class MessageResponse(BaseModel):
    message: str


class SummaryResponse(BaseModel):
    students_count: int
    professors_count: int
    courses_count: int
    selections_count: int
    assigned_courses_count: int
    total_capacity: int
    remaining_capacity: int


class AllDataResponse(BaseModel):
    students: list[StudentResponse]
    professors: list[ProfessorResponse]
    courses: list[CourseResponse]
