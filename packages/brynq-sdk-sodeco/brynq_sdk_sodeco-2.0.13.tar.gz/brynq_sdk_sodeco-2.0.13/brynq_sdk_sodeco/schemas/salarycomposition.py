from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class SalaryCompositionSchema(DataFrameModel):
    """Schema for salary composition entries"""
    # Required fields
    Startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Code: int = Field(nullable=False, ge=1, le=8999)
    
    # Optional fields
    Enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Days: Optional[int] = Field(nullable=True, ge=0, le=99)
    Hours: Optional[float] = Field(nullable=True, ge=0.0, le=9999.0)
    Unity: Optional[float] = Field(nullable=True)
    Percentage: Optional[float] = Field(nullable=True)
    Amount: Optional[float] = Field(nullable=True)
    Supplement: Optional[float] = Field(nullable=True)
    TypeOfIndexing: Optional[str] = Field(nullable=True, isin=[
        'NoIndexation', 'Indexation', 'FrozenSalary', 'SalaryAboveScale'
    ])
