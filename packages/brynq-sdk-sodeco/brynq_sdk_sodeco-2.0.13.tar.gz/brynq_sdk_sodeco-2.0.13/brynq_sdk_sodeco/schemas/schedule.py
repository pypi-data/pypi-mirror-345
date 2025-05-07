from pandera import DataFrameModel, Field, Column
from typing import Optional, List
import pandas as pd

class ScheduleWeekSchema(DataFrameModel):
    """Schema for schedule week entries"""
    WeekNumber: int = Field(nullable=False, ge=1, le=15)
    Day1: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)
    Day2: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)
    Day3: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)
    Day4: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)
    Day5: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)
    Day6: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)
    Day7: Optional[float] = Field(nullable=True, ge=0.0, le=24.0)

    class Config:
        strict = True
        coerce = True

class ScheduleSchema(DataFrameModel):
    """Schema for schedule entries"""
    ScheduleID: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 4})
    Description: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 50})
    StartDate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Week: List[dict] = Field(nullable=False)  # List of ScheduleWeek objects
    
    class Config:
        strict = True
        coerce = True
    
    @classmethod
    def validate_weeks(cls, weeks: List[dict]) -> bool:
        """Validate a list of schedule weeks against the ScheduleWeekSchema"""
        if not weeks:
            return False
            
        try:
            df = pd.DataFrame(weeks)
            ScheduleWeekSchema.validate(df)
            return True
        except Exception:
            return False
