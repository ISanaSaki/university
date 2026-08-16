from typing import Optional

from pydantic import BaseModel, Field

from schemas.base_schema import InputModel


class ProfessorCreate(InputModel):
    national_id: str = Field(..., min_length=3, max_length=20)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    personnel_code: str = Field(..., min_length=3, max_length=20)
    department: str = Field(..., min_length=2, max_length=80)


class ProfessorUpdate(InputModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    personnel_code: Optional[str] = Field(None, min_length=3, max_length=20)
    department: Optional[str] = Field(None, min_length=2, max_length=80)


class ProfessorResponse(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    personnel_code: str
    department: str
    courses: list[str] = Field(default_factory=list)
