from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator

from schemas.base_schema import InputModel


class StudentCreate(InputModel):
    national_id: str = Field(..., min_length=10, max_length=10)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=50)
    student_number: str = Field(..., min_length=8, max_length=12)
    major: str = Field(..., min_length=3, max_length=80)

    @field_validator("national_id", "student_number")
    @classmethod
    def validate_numbers(cls, value):
        if not value.isdigit():
            raise ValueError("must contain only digits")
        return value

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value):
        if not re.match(r"^[A-Za-zآ-ی\s-]+$", value):
            raise ValueError("name contains invalid characters")
        return value


class StudentUpdate(InputModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=40)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    student_number: Optional[str] = Field(None, min_length=8, max_length=12)
    major: Optional[str] = Field(None, min_length=3, max_length=80)

    @field_validator("student_number")
    @classmethod
    def validate_student_number(cls, value):
        if value and not value.isdigit():
            raise ValueError("student number must be numeric")
        return value


class StudentResponse(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    student_number: str
    major: str
    selected_courses: list[str] = Field(default_factory=list)
