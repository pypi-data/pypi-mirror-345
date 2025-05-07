from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum


class ResetEnum(str, Enum):
    NO = 'N'
    YES = 'Y'


class CostModel(BaseModel):
    """Model for cost entries in prestations"""
    Code: int = Field(..., ge=1, le=8999)  # Required field
    CostCentre: Optional[str] = Field(None, min_length=0, max_length=15)
    Shift: Optional[int] = Field(None, ge=1, le=99)
    Days: Optional[int] = Field(None, ge=0, le=99)
    Hours: Optional[float] = Field(None, ge=0, le=9999)
    Unity: Optional[float] = None
    Percentage: Optional[float] = None
    Amount: Optional[float] = None
    Supplement: Optional[float] = None


class PrestationEntryModel(BaseModel):
    """Model for individual prestation entries"""
    Day: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')  # Required field
    Code: int = Field(..., ge=1, le=6999)  # Required field
    CostCentre: Optional[str] = Field(None, min_length=0, max_length=15)
    Shift: Optional[int] = Field(None, ge=1, le=99)
    Hours: Optional[float] = Field(None, ge=0, le=9999)


class PrestationModel(BaseModel):
    """Model for prestation entries"""
    # Required fields
    WorkerNumber: int = Field(..., ge=1, le=9999999)
    Month: int = Field(..., ge=1, le=12)
    Year: int = Field(..., ge=1900, le=2075)
    EndOfPeriod: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    
    # Optional fields
    Annotation: Optional[str] = None
    Reset: Optional[ResetEnum] = None
    Prestations: Optional[List[Union[PrestationEntryModel, None]]] = None
    Costs: Optional[List[Union[CostModel, None]]] = None


class PrestationCompletedModel(BaseModel):
    """Model for marking prestations as completed"""
    Month: int = Field(..., ge=1, le=12)
    Year: int = Field(..., ge=1900, le=2075)
    Correction: Optional[ResetEnum] = None

    @classmethod
    def validate_completed(cls, data: dict) -> bool:
        try:
            PrestationCompletedModel(**data)
            return True
        except Exception:
            return False


class DeletePrestationModel(BaseModel):
    """Model for deleting prestations"""
    WorkerNumber: int = Field(..., ge=1, le=9999999)
    Month: int = Field(..., ge=1, le=12)
    Year: int = Field(..., ge=1900, le=2075)

    @classmethod
    def validate_delete(cls, data: dict) -> bool:
        try:
            DeletePrestationModel(**data)
            return True
        except Exception:
            return False
