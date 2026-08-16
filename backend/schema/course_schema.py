from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator

from schemas.base_schema import InputModel


class CourseCreate(InputModel):
    course_id: str = Field(..., min_length=3, max_length=20)
    title: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=10)
    unit: int = Field(..., ge=1, le=4, strict=True)
    capacity: int = Field(..., ge=1, le=100, strict=True)

    @field_validator("course_id", "code")
    @classmethod
    def validate_codes(cls, value):
        if not re.match(r"^[A-Za-z0-9_-]+$", value):
            raise ValueError("invalid course code format")
        return value


class CourseUpdate(InputModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    code: Optional[str] = Field(None, min_length=3, max_length=10)
    unit: Optional[int] = Field(None, ge=1, le=4, strict=True)
    capacity: Optional[int] = Field(None, ge=1, le=100, strict=True)


class CourseResponse(BaseModel):
    course_id: str
    title: str
    code: str
    unit: int
    capacity: int
    professor: Optional[str] = None
    students: list[str] = Field(default_factory=list)
