from typing import Optional

from pydantic import BaseModel, Field

from schemas.base_schema import InputModel


class CourseCreate(InputModel):
    course_id: str = Field(..., min_length=2, max_length=20)
    title: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    unit: int = Field(..., ge=1, le=5, strict=True)
    capacity: int = Field(..., ge=1, le=200, strict=True)


class CourseUpdate(InputModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    unit: Optional[int] = Field(None, ge=1, le=5, strict=True)
    capacity: Optional[int] = Field(None, ge=1, le=200, strict=True)


class CourseResponse(BaseModel):
    course_id: str
    title: str
    code: str
    unit: int
    capacity: int
    professor: Optional[str] = None
    students: list[str] = Field(default_factory=list)
