from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class DivergentPaymentSchema(DataFrameModel):
    """Schema for divergent payment entries"""
    # Required fields
    Startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Enddate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    PayoutType: str = Field(nullable=False, isin=['Salarycode', 'Amount', 'Percentage'])
    Amount: float = Field(nullable=False, ge=0.0, le=10000.0)
    PayWay: str = Field(nullable=False, isin=['Cash', 'Transfer', 'Electronic', 'AssignmentList'])
    BankAccount: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 45})
    BICCode: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 15})
    
    # Optional fields
    SalaryCode: Optional[int] = Field(nullable=True, ge=1, le=8999)
    Beneficiary: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    Street: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    HouseNumber: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5})
    PostBox: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5})
    ZIPCode: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 12})
    City: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    Reference: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
