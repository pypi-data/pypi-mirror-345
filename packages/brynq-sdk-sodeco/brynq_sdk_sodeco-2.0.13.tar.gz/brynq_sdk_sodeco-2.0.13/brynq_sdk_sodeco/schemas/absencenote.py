from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class AbsenceNoteSchema(DataFrameModel):
    """Schema for absence note entries"""
    # Required fields
    Notedate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Enddate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    
    # Optional fields
    Reason: Optional[str] = Field(nullable=True, isin=['Sickness', 'Accident', 'Extension'])
    MayLeaveHouse: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    Resumedate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Resume: Optional[str] = Field(nullable=True, isin=['None', 'Full', 'Partial'])
    SalaryCode: Optional[int] = Field(nullable=True, ge=800, le=899)
