from pandera import DataFrameModel, Field, Column
from typing import Optional
from datetime import datetime

class CarSchema(DataFrameModel):
    """Schema for company car entries"""
    # Required fields
    StartingDate: str = Field(nullable=False, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    LicensePlate: str = Field(nullable=False, str_length={'min_value': 0, 'max_value': 15})
    
    # Optional fields
    EndingDate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    WorkerId: Optional[int] = Field(nullable=True)
    CatRSZ: Optional[str] = Field(nullable=True, str_length={'min_value': 3, 'max_value': 3}, regex=r'^[0-9]*$')
    MotorType: Optional[str] = Field(nullable=True, isin=['Gasoline', 'Diesel', 'LPG', 'Electric', 'CNG'])
    TaxHorsepower: Optional[int] = Field(nullable=True, ge=0, le=99)
    Co2EmissionsHybrideWLTP: Optional[int] = Field(nullable=True, ge=0, le=500)
    Co2EmissionsHybride: Optional[int] = Field(nullable=True, ge=0, le=500)
    Co2EmissionsWLTP: Optional[int] = Field(nullable=True, ge=0, le=500)
    Co2Emissions: Optional[int] = Field(nullable=True, ge=0, le=500)
    Code: Optional[int] = Field(nullable=True, ge=4000, le=8999)
    FuelCard: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 20})
    Brand: Optional[str] = Field(nullable=True, str_length={'min_value': 0, 'max_value': 50})
    OrderDate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    RegistrationDate: Optional[str] = Field(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    CatalogPrice: Optional[float] = Field(nullable=True)
    LightTruck: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    Informative: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    PoolCar: Optional[str] = Field(nullable=True, isin=['N', 'Y'])
    PersContributionAmount: Optional[float] = Field(nullable=True)
    PersContributionPercentage: Optional[float] = Field(nullable=True)
    PersContributionCode: Optional[int] = Field(nullable=True, ge=4000, le=8999)

    class Config:
        strict = True
        coerce = True
