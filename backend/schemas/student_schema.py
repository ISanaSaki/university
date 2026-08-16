from typing import Optional

from pydantic import BaseModel, Field

from schemas.base_schema import InputModel


class StudentCreate(InputModel):
    national_id: str = Field(..., min_length=3, max_length=20)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    student_number: str = Field(..., min_length=3, max_length=20)
    major: str = Field(..., min_length=2, max_length=80)


class StudentUpdate(InputModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    student_number: Optional[str] = Field(None, min_length=3, max_length=20)
    major: Optional[str] = Field(None, min_length=2, max_length=80)


class StudentResponse(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    student_number: str
    major: str
    selected_courses: list[str] = Field(default_factory=list)
