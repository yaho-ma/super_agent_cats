from typing import Optional, List

from pydantic import BaseModel, Field


class CatSchema(BaseModel):
    id: Optional[int]
    name: str
    years_of_experience: int
    breed: str
    salary: float


class UpdateSalaryRequest(BaseModel):
    salary: float


class TargetSchema(BaseModel):
    name: str
    country: str
    notes: Optional[str] = None
    complete: bool = False

    class Config:
        orm_mode = True


class MissionSchema(BaseModel):
    id: Optional[int]
    cat_id: Optional[int] = None
    complete: bool = False
    targets: List[TargetSchema]

    class Config:
        orm_mode = True


class UpdateTargetSchema(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    complete: Optional[bool] = None

    class Config:
        orm_mode = True
