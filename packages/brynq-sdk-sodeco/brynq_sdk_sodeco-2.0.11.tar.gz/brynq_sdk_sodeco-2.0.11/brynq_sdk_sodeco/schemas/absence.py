from pandera import DataFrameModel, Field, Column
from typing import Optional, List
from datetime import datetime
import pandas as pd

class AbsenceSchema(DataFrameModel):
    """Schema for individual absence entries"""
    # Required fields
    Day: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Code: int = Field(nullable=False, ge=1, le=6999)
    
    # Optional fields
    Shift: Optional[pd.Int64Dtype] = Field(nullable=True, ge=1, le=99)
    Hours: Optional[float] = Field(nullable=True, ge=0.0, le=23.99)

    class Config:
        strict = True
        coerce = True

class AbsencesSchema(DataFrameModel):
    """Schema for worker absences list"""
    # Required fields
    WorkerNumber: int = Field(nullable=False, ge=1, le=9999999)
    Absences: List[dict] = Field(nullable=False)  # Will be validated separately using AbsenceSchema

    class Config:
        strict = True
        coerce = True
