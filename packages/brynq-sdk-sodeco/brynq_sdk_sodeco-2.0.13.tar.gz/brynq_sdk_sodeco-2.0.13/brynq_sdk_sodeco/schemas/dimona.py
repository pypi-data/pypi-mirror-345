from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime
import pandas as pd


class UsingDataSchema(DataFrameModel):
    """Schema for using data in Dimona"""
    # All fields are optional
    UsingJointCommissionNbr: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, regex=r'^[0-9,.]*$')
    UsingEmployerName: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 40})
    UsingEmployerCompanyID: Optional[float] = Field(nullable=True, ge=0.0, le=9999999999.0)
    UsingStreet: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100})
    UsingHouseNumber: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 10})
    UsingPostBox: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5})
    UsingZIPCode: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 12})
    UsingCity: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    UsingCountry: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150")

    class Config:
        strict = True
        coerce = True

class GetDimonaSchema(DataFrameModel):
    """Schema for GET Dimona entries"""
    # Required fields
    StartingDate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    
    # Optional fields
    DimonaPeriodId: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0)
    EndingDate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    StartingHour: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$')
    EndingHour: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$')
    FirstMonthC32ANbr: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0)
    NextMonthC32ANbr: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0)
    PlannedHoursNbr: Optional[pd.Int64Dtype] = Field(nullable=True, ge=0, le=999)
    UsingData: Optional[dict] = Field(nullable=True)  # Will be validated separately using UsingDataSchema
    Receipt: Optional[float] = Field(nullable=True, ge=0.0, le=999999999999.0)
    JointCommissionNbr: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 6}, regex=r'^[0-9,.]*$')
    WorkerType: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3})
    LastAction: Optional[str] = Field(nullable=True, str_length={'min_value': 1, 'max_value': 1})
    ExceedingHoursNbr: Optional[pd.Int64Dtype] = Field(nullable=True, ge=0, le=999)
    QuotaExceeded: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    Belated: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    Status: Optional[str] = Field(nullable=True, isin=['Blocked', 'InProgress', 'OK', 'Error'])
    Error: Optional[str] = Field(nullable=True)

    class Config:
        strict = True
        coerce = True

class PostDimonaSchema(GetDimonaSchema):
    """Schema for POST Dimona entries, extends GetDimonaSchema with additional required fields"""
    # Additional required fields for POST
    NatureDeclaration: str = Field(nullable=False, isin=['DimonaIn', 'DimonaOut', 'DimonaModification', 'DimonaCancel'])
    Email: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 100})
    
    # Additional optional fields for POST
    ContractType: str = Field(nullable=True, isin=['Normal', 'Extra', 'Apprentice', 'IBO', 'TRI', 'DWD', 'A17', 'Flex', 'STG', 'S17', 'O17'])
    Name: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 40})
    Firstname: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 25})
    Initial: Optional[str] = Field(nullable=True, str_length={'min_value': 1, 'max_value': 1})
    INSS: Optional[float] = Field(nullable=True, ge=0.0, le=99999999999.0)
    Sex: Optional[str] = Field(nullable=True, isin=['M', 'F'])
    Birthdate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    Birthplace: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    BirthplaceCountry: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150")
    Nationality: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150")
    Street: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 100})
    HouseNumber: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 10})
    PostBox: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 5})
    ZIPCode: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 12})
    City: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    Country: Optional[str] = Field(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default="00150")
    CatRSZ: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, regex=r'^[0-9]*$')
    Student: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    ActivityWithRisk: Optional[pd.Int64Dtype] = Field(nullable=True)
    WorkerStatus: Optional[str] = Field(nullable=True, isin=['F1', 'F2'])
    EmploymentNature: Optional[str] = Field(nullable=True, isin=['Employee', 'Worker'])
    StartingHour2: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$')
    EndingHour2: Optional[str] = Field(nullable=True, str_length={'min_value': 12, 'max_value': 12}, regex=r'^[0-9]*$')

    class Config:
        strict = True
        coerce = True
