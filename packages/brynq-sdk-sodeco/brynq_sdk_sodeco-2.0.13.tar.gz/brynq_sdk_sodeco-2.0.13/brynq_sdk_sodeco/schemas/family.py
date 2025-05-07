from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class FamilySchema(DataFrameModel):
    # Required fields
    Startdate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    
    # Optional fields (CivilStatus is now optional according to the latest schema)
    CivilStatus: Optional[str] = Field(nullable=True, isin=[
        'Single', 'Married', 'Widow', 'Divorced', 'Separated',
        'Cohabitation', 'LiveTogether'
    ])
    Enddate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    WorkerHandicapped: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    WorkerSingleWithChildren: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    SpouseWithIncome: Optional[str] = Field(nullable=True, isin=[
        'WithIncome', 'WithoutIncome', 'ProffIncomeLessThan235',
        'ProffIncomeLessThan141', 'ProffIncomeLessThan469'
    ])
    SpouseHandicapped: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    SpouseName: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 40})
    SpouseFirstname: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 25})
    SpouseINSS: Optional[float] = Field(nullable=True, ge=0, le=99999999999.0)
    SpouseSex: Optional[str] = Field(nullable=True, isin=['M', 'F'])
    SpouseProfession: Optional[str] = Field(nullable=True, isin=[
        'Handworker', 'Servant', 'Employee', 'SelfEmployed', 'Miner',
        'Sailor', 'CivilServant', 'Other', 'Nil'
    ])
    SpouseBirthdate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    SpouseBirthplace: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    
    # Integer fields with min/max values
    ChildrenAtCharge: Optional[int] = Field(nullable=True, ge=0, le=99)
    ChildrenHandicapped: Optional[int] = Field(nullable=True, ge=0, le=99)
    OthersAtCharge: Optional[int] = Field(nullable=True, ge=0, le=99)
    OthersHandicapped: Optional[int] = Field(nullable=True, ge=0, le=99)
    Others65AtCharge: Optional[int] = Field(nullable=True, ge=0, le=99)
    # Added missing field from the latest schema
    WageGarnishmentChildrenAtCharge: Optional[int] = Field(nullable=True, ge=0, le=99)
    Others65Handicapped: Optional[int] = Field(nullable=True, ge=0, le=99)
    Others65NeedOfCare: Optional[int] = Field(nullable=True, ge=0, le=99)
    ChildBenefitInstitution: Optional[int] = Field(nullable=True, ge=0, le=9999)
    
    # Additional optional fields
    ChildBenefitReference: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 15})
    Weddingdate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
