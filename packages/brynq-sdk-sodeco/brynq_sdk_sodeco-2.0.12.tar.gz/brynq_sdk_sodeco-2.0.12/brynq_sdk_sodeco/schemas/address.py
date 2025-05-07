from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class AddressSchema(DataFrameModel):
    # Required fields
    Startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Street: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 100})
    HouseNumber: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 10})
    ZIPCode: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 12})
    City: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 30})
    Country: str = Field(nullable=False, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default='00150')
    
    # Optional fields
    Enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    PostBox: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5})
    Distance: Optional[float] = Field(nullable=True, ge=0.0, le=99999.9)
