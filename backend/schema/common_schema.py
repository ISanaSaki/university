from pydantic import BaseModel, Field

from schemas.course_schema import CourseResponse
from schemas.professor_schema import ProfessorResponse
from schemas.student_schema import StudentResponse


class MessageResponse(BaseModel):
    message: str = Field(..., min_length=1)


class SummaryResponse(BaseModel):
    students_count: int = Field(ge=0)
    professors_count: int = Field(ge=0)
    courses_count: int = Field(ge=0)
    selections_count: int = Field(ge=0)
    assigned_courses_count: int = Field(ge=0)
    total_capacity: int = Field(ge=0)
    remaining_capacity: int = Field(ge=0)


class AllDataResponse(BaseModel):
    students: list[StudentResponse]
    professors: list[ProfessorResponse]
    courses: list[CourseResponse]
