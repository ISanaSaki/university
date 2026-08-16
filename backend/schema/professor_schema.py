from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator

from schemas.base_schema import InputModel


class ProfessorCreate(InputModel):
    national_id: str = Field(..., min_length=10, max_length=10)
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=50)
    personnel_code: str = Field(..., min_length=4, max_length=12)
    department: str = Field(..., min_length=3, max_length=80)

    @field_validator("national_id", "personnel_code")
    @classmethod
    def validate_codes(cls, value):
        if not value.isdigit():
            raise ValueError("code must contain only digits")
        return value

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value):
        if not re.match(r"^[A-Za-zآ-ی\s-]+$", value):
            raise ValueError("name contains invalid characters")
        return value


class ProfessorUpdate(InputModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=40)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    personnel_code: Optional[str] = Field(None, min_length=4, max_length=12)
    department: Optional[str] = Field(None, min_length=3, max_length=80)


class ProfessorResponse(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    personnel_code: str
    department: str
    courses: list[str] = Field(default_factory=list)
