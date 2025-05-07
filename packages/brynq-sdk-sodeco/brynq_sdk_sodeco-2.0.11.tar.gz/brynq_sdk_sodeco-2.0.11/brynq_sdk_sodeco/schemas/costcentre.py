from pandera import DataFrameModel, Field, Column
from typing import Optional
import pandas as pd

class CostCentreItemSchema(DataFrameModel):
    """Schema for individual cost centre entries"""
    CostCentre: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 15})
    Percentage: float = Field(nullable=False, ge=0.0, le=100.0)

class CostCentreSchema(DataFrameModel):
    """Schema for cost centre entries"""
    Startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    
    @classmethod
    def validate_cost_centres(cls, cost_centres: list) -> bool:
        """Validate a list of cost centres against the CostCentreItemSchema"""
        if not cost_centres:
            return False
            
        try:
            df = pd.DataFrame(cost_centres)
            CostCentreItemSchema.validate(df)
            
            # Additional validation: sum of percentages should be 100%
            total_percentage = df['Percentage'].sum()
            if not (99.99 <= total_percentage <= 100.01):  # Allow for small floating point differences
                return False
                
            return True
        except Exception:
            return False
