from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class CommunicationSchema(DataFrameModel):
    # Required fields
    CommunicationType: str = Field(nullable=False, isin=[
        'None', 'Phone', 'GSM', 'Email', 'PrivatePhone', 'Fax',
        'InternalPhone', 'PrivateEmail', 'GSMEntreprise', 'Website'
    ])
    Value: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 100})
    
    # Optional fields
    ID: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100})
    ContactPerson: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100})
    ContactPersonFirstname: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 50})
