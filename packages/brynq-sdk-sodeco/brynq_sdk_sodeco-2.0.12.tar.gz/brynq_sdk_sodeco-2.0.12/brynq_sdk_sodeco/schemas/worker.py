from pandera import DataFrameModel, Field as PanderaField, Check
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


class GetWorkerSchema(DataFrameModel):
    # Required fields
    Name: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 40})
    Firstname: str = PanderaField(nullable=False, str_length={'min_value': 0, 'max_value': 25})

    # Optional fields with specific validations
    INSS: Optional[float] = PanderaField(nullable=True, ge=0.0, le=99999999999.0)
    Sex: Optional[str] = PanderaField(nullable=True, isin=['M', 'F'])
    Birthdate: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    BirthplaceZIPCode: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 12})
    Birthplace: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 30})
    BirthplaceCountry: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default='00150')
    Nationality: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 5, 'max_value': 5}, regex=r'^[0-9]*$', default='00150')
    Language: Optional[str] = PanderaField(nullable=True, isin=['N', 'F', 'D', 'E'])
    PayWay: Optional[str] = PanderaField(nullable=True, isin=['Cash', 'Transfer', 'Electronic', 'AssignmentList'])
    BankAccount: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 45})
    BICCode: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15})
    ID: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15})
    IDType: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 3})
    IDValidUntil: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    DriverLicense: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15})
    DriverCategory: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 2})
    NumberPlate: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10})
    FuelCard: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20})
    Education: Optional[str] = PanderaField(nullable=True, isin=[
        'Basic', 'LowerSecondary', 'HigherSecondary', 'NotUniversity',
        'University', 'Secondary1Degree', 'Secondary2Degree', 'Secondary3Degree', 'Unknown'
    ])
    Profession: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50})
    EHealthInsurance: Optional[int] = PanderaField(nullable=True, ge=0, le=9999)
    EHealthInsuranceReference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 20})
    AccidentInsurance: Optional[int] = PanderaField(nullable=True, ge=0, le=9999)
    MedicalCenter: Optional[int] = PanderaField(nullable=True, ge=0, le=9999)
    MedicalCenterReference: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 15})
    ExternalID: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 50})
    InterimFrom: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    InterimTo: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 8, 'max_value': 8}, regex=r'^[0-9]*$')
    TravelExpenses: Optional[str] = PanderaField(nullable=True, isin=[
        'PublicTransportTrain', 'OwnTransport', 'PublicTransportOther', 'Bicycle', 'None'
    ])
    TypeOfTravelExpenses: Optional[str] = PanderaField(nullable=True, isin=[
        'Other', 'PublicCommonTransport', 'OrganisedCommonTransport'
    ])
    SalaryCodeTravelExpenses: Optional[int] = PanderaField(nullable=True, ge=1, le=9999)
    MainDivision: Optional[str] = PanderaField(nullable=True, str_length={'min_value': 0, 'max_value': 10})

    class Config:
        strict = True
        coerce = True


class ExistEnum(str, Enum):
    NO = 'N'
    YES = 'Y'


class CareerBreakKindEnum(str, Enum):
    FULLTIME = 'Fulltime'
    PART_TIME_ONE_FIFTH = 'PartTimeOneFifth'
    PART_TIME_ONE_QUARTER = 'PartTimeOneQuarter'
    PART_TIME_ONE_THIRD = 'PartTimeOneThird'
    PART_TIME_HALF = 'PartTimeHalf'
    PART_TIME_THREE_FIFTHS = 'PartTimeThreeFifths'
    PART_TIME_ONE_TENTH = 'PartTimeOneTenth'


class CareerBreakReasonEnum(str, Enum):
    PALLIATIVE_CARE = 'PalliativeCare'
    SERIOUSLY_ILL = 'SeriouslyIll'
    OTHER = 'Other'
    PARENTAL_LEAVE = 'ParentalLeave'
    CRISIS = 'Crisis'
    FAMILY_CARE = 'FamilyCare'
    END_OF_CAREER = 'EndOfCareer'
    SICK_CHILD = 'SickChild'
    FAMILY_CARE_CORONA = 'FamilyCareCorona'
    CHILD_CARE_UNDER_8 = 'ChildCareUnder8'
    CHILD_CARE_HANDICAP_UNDER_21 = 'ChildCareHandicapUnder21'
    CERTIFIED_TRAINING = 'CertifiedTraining'


class ContractTypeEnum(str, Enum):
    FULLTIME = 'Fulltime'
    PART_TIME = 'PartTime'


class CivilStatusEnum(str, Enum):
    SINGLE = 'Single'
    MARRIED = 'Married'
    WIDOW = 'Widow'
    DIVORCED = 'Divorced'
    SEPARATED = 'Separated'
    COHABITATION = 'Cohabitation'
    LIVE_TOGETHER = 'LiveTogether'


class SpouseIncomeEnum(str, Enum):
    WITH_INCOME = 'WithIncome'
    WITHOUT_INCOME = 'WithoutIncome'
    PROFF_INCOME_LESS_THAN_235 = 'ProffIncomeLessThan235'
    PROFF_INCOME_LESS_THAN_141 = 'ProffIncomeLessThan141'
    PROFF_INCOME_LESS_THAN_469 = 'ProffIncomeLessThan469'


class SpouseProfessionEnum(str, Enum):
    HANDWORKER = 'Handworker'
    SERVANT = 'Servant'
    EMPLOYEE = 'Employee'
    SELF_EMPLOYED = 'SelfEmployed'
    MINER = 'Miner'
    SAILOR = 'Sailor'
    CIVIL_SERVANT = 'CivilServant'
    OTHER = 'Other'
    NIL = 'Nil'


class TaxCalculationEnum(str, Enum):
    NORMAL = 'Normal'
    CONVERSION_PT = 'ConversionPT'
    FISC_VOL_AMOUNT = 'FiscVolAmount'
    FISC_VOL_PERCENT = 'FiscVolPercent'
    AMOUNT = 'Amount'
    PERCENT = 'Percent'
    PERCENT_NORMAL = 'PercentNormal'
    NON_RESIDENT = 'NonResident'
    NO_CITY = 'NoCity'
    NO_TAX = 'NoTax'
    YOUNGER = 'Younger'
    NORMAL_PLUS = 'NormalPlus'
    TRAINER = 'Trainer'
    NORMAL_MIN_PERC = 'NormalMinPerc'
    NORMAL_MIN_AMOUNT = 'NormalMinAmount'


class CareerBreakDefinition(BaseModel):
    Exist: ExistEnum
    Kind: Optional[CareerBreakKindEnum] = None
    Reason: Optional[CareerBreakReasonEnum] = None
    OriginallyContractType: Optional[ContractTypeEnum] = None
    WeekhoursWorkerBefore: Optional[float] = None
    WeekhoursEmployerBefore: Optional[float] = None


class CertainWorkDefinition(BaseModel):
    Exist: ExistEnum
    Description: Optional[str] = Field(None, min_length=0, max_length=250)


class Address(BaseModel):
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Street: str = Field(..., min_length=0, max_length=100)
    HouseNumber: str = Field(..., min_length=0, max_length=10)
    PostBox: Optional[str] = Field(None, min_length=0, max_length=5)
    ZIPCode: str = Field(..., min_length=0, max_length=12)
    City: str = Field(..., min_length=0, max_length=30)
    Country: str = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$')
    Distance: Optional[float] = Field(None, ge=0.0, le=99999.9)


class CommunicationModel(BaseModel):
    CommunicationType: Literal['None', 'Phone', 'GSM', 'Email', 'PrivatePhone',
    'Fax', 'InternalPhone', 'PrivateEmail', 'GSMEntreprise',
    'Website']
    Value: str = Field(..., min_length=0, max_length=100)
    ContactPerson: Optional[str] = Field(None, min_length=0, max_length=100)


EmploymentStatusType = Literal['Workman', 'Employee', 'Director']
ContractLiteral = Literal[
    'Usually', 'FlexiVerbal', 'FlexiWritten', 'FlexiLiable', 'Sportsperson',
    'Housekeeper', 'Servant', 'Agriculture', 'Homework', 'HomeworkChildcare',
    'Physician', 'PhysicianTraining', 'PhysicianIndependant', 'ApprenticeFlemisch',
    'ApprenticeFrench', 'ApprenticeGerman', 'ApprenticeManager', 'ApprenticeIndustrial',
    'ApprenticeSocio', 'ApprenticeBio', 'ApprenticeAlternating', 'EarlyRetirement',
    'EarlyRetirementPartTime', 'FreeNOSS', 'FreeNOSSManager', 'FreeNOSSOther',
    'FreeNOSSSportingEvent', 'FreeNOSSHelper', 'FreeNOSSSocio', 'FreeNOSSEducation',
    'FreeNOSSSpecialCultures', 'FreeNOSSVolunteer', 'Horeca', 'HorecaExtraHourLiable',
    'HorecaExtraDayLiable', 'HorecaExtraHourForfait', 'HorecaExtraDayForfait',
    'HorecaFlexiVerbal', 'HorecaFlexiWritten', 'HorecaFlexiLiable', 'Construction',
    'ConstructionAlternating', 'ConstructionApprenticeYounger', 'ConstructionApprentice',
    'ConstructionGodfather', 'JobTrainingIBO', 'JobTrainingSchool', 'JobTrainingVDAB',
    'JobTrainingLiberalProfession', 'JobTrainingEntry', 'JobTrainingPFIWa',
    'JobTrainingABO', 'JobTrainingPFIBx', 'JobTrainingBIO', 'JobTrainingAlternating',
    'JobTrainingDisability', 'NonProfitRiziv', 'NonProfitGesco', 'NonProfitDAC',
    'NonProfitPrime', 'NonProfitLowSkilled', 'Artist', 'ArtistWithContract',
    'ArtistWithoutContract', 'Transport', 'TransportNonMobile', 'TransportGarage',
    'Aircrew', 'AircrewPilot', 'AircrewCabinCrew', 'Interim', 'InterimTemporary',
    'InterimsPermanent', 'External', 'ExternalApplicant', 'ExternalSubcontractor',
    'ExternalAgentIndependant', 'ExternalExtern', 'ExternalIntern', 'ExternalLegalPerson',
    'SalesRepresentative', 'SportsTrainer'
]


class Contract(BaseModel):
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    EmploymentStatus: Optional[EmploymentStatusType] = None
    Contract: Optional[ContractLiteral] = None
    CareerBreak: Optional[CareerBreakDefinition] = None
    CertainWork: Optional[CertainWorkDefinition] = None


class FamilyStatus(BaseModel):
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    CivilStatus: Optional[CivilStatusEnum] = None
    WorkerHandicapped: Optional[ExistEnum] = None
    WorkerSingleWithChildren: Optional[ExistEnum] = None
    SpouseWithIncome: Optional[SpouseIncomeEnum] = None
    SpouseHandicapped: Optional[ExistEnum] = None
    SpouseName: Optional[str] = Field(None, min_length=0, max_length=40)
    SpouseFirstname: Optional[str] = Field(None, min_length=0, max_length=25)
    SpouseINSS: Optional[float] = Field(None, ge=0.0, le=99999999999.0)
    SpouseSex: Optional[Literal['M', 'F']] = None
    SpouseBirthdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    SpouseProfession: Optional[SpouseProfessionEnum] = None
    SpouseBirthplace: Optional[str] = Field(None, min_length=0, max_length=30)
    ChildrenAtCharge: Optional[int] = Field(None, ge=0, le=99)
    ChildrenHandicapped: Optional[int] = Field(None, ge=0, le=99)
    OthersAtCharge: Optional[int] = Field(None, ge=0, le=99)
    OthersHandicapped: Optional[int] = Field(None, ge=0, le=99)
    Others65AtCharge: Optional[int] = Field(None, ge=0, le=99)
    Others65Handicapped: Optional[int] = Field(None, ge=0, le=99)
    ChildBenefitInstitution: Optional[int] = Field(None, ge=0, le=9999)
    ChildBenefitReference: Optional[str] = Field(None, min_length=0, max_length=15)
    Weddingdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')


class TaxModel(BaseModel):
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    TaxCalculation: TaxCalculationEnum
    Value: Optional[float] = Field(None, ge=0.0, le=9999999999.0)


class ReplacementModel(BaseModel):
    WorkerNumber: int = Field(..., ge=1, le=9999999)
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class PostWorkerSchema(BaseModel):
    # Required fields
    WorkerNumber: int = Field(..., ge=1, le=9999999)
    Name: str = Field(..., min_length=0, max_length=40)
    Firstname: str = Field(..., min_length=0, max_length=25)

    # Optional basic fields
    Initial: Optional[str] = Field(None, min_length=1, max_length=1)
    INSS: Optional[float] = Field(None, ge=0.0, le=99999999999.0)
    Sex: Optional[Literal['M', 'F']] = None
    Birthdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    BirthplaceZIPCode: Optional[str] = Field(None, min_length=0, max_length=12)
    Birthplace: Optional[str] = Field(None, min_length=0, max_length=30)
    BirthplaceCountry: Optional[str] = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$')
    Nationality: Optional[str] = Field(default='00150', min_length=5, max_length=5, pattern=r'^[0-9]*$')
    Language: Optional[Literal['N', 'F', 'D', 'E']] = None
    PayWay: Optional[Literal['Cash', 'Transfer', 'Electronic', 'AssignmentList']] = None
    BankAccount: Optional[str] = Field(None, min_length=0, max_length=45)
    BICCode: Optional[str] = Field(None, min_length=0, max_length=15)
    ID: Optional[str] = Field(None, min_length=0, max_length=15)
    IDType: Optional[str] = Field(None, min_length=0, max_length=3)
    IDValidUntil: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    DriverLicense: Optional[str] = Field(None, min_length=0, max_length=15)
    DriverCategory: Optional[str] = Field(None, min_length=0, max_length=2)
    NumberPlate: Optional[str] = Field(None, min_length=0, max_length=10)
    FuelCard: Optional[str] = Field(None, min_length=0, max_length=20)
    Education: Optional[Literal[
        'Basic', 'LowerSecondary', 'HigherSecondary', 'NotUniversity',
        'University', 'Secondary1Degree', 'Secondary2Degree', 'Secondary3Degree', 'Unknown'
    ]] = None
    Profession: Optional[str] = Field(None, min_length=0, max_length=50)
    EHealthInsurance: Optional[int] = Field(None, ge=0, le=9999)
    EHealthInsuranceReference: Optional[str] = Field(None, min_length=0, max_length=20)
    AccidentInsurance: Optional[int] = Field(None, ge=0, le=9999)
    MedicalCenter: Optional[int] = Field(None, ge=0, le=9999)
    MedicalCenterReference: Optional[str] = Field(None, min_length=0, max_length=15)
    ExternalID: Optional[str] = Field(None, min_length=0, max_length=50)
    InterimFrom: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    InterimTo: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    TravelExpenses: Optional[Literal[
        'PublicTransportTrain', 'OwnTransport', 'PublicTransportOther',
        'Bicycle', 'None'
    ]] = None
    TypeOfTravelExpenses: Optional[Literal[
        'Other', 'PublicCommonTransport', 'OrganisedCommonTransport'
    ]] = None
    SalaryCodeTravelExpenses: Optional[int] = Field(None, ge=1, le=9999)

    # Required nested schemas
    address: List[Address]
    FamilyStatus: List[FamilyStatus]
    contract: List[Contract]

    # Optional nested schemas
    Communication: Optional[List[CommunicationModel] | None] = None
    Tax: Optional[List[TaxModel] | None] = None
    Replacement: Optional[List[ReplacementModel] | None] = None
