from typing import Optional, List

from pydantic import BaseModel, Field


class CatSchema(BaseModel):
    id: Optional[int]
    name: str = Field(..., min_length=1, max_length=100)
    years_of_experience: int = Field(..., ge=0)
    breed: str = Field(..., min_length=1, max_length=50)
    salary: float = Field(..., gt=0)


class UpdateSalaryRequest(BaseModel):
    salary: float = Field(..., gt=0)


class TargetSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    complete: bool = False

    class Config:
        orm_mode = True


class MissionSchema(BaseModel):
    id: Optional[int]
    cat_id: Optional[int] = Field(None, ge=1)
    complete: bool = False
    targets: List[TargetSchema] = Field(..., min_items=1)

    class Config:
        orm_mode = True


class UpdateTargetSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str]  = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    complete: Optional[bool] = None

    class Config:
        orm_mode = True
