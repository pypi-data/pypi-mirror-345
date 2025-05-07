from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ResetEnum(str, Enum):
    N = "N"
    Y = "Y"


class ContractTypeEnum(str, Enum):
    WORKMAN = "Workman"
    EMPLOYEE = "Employee"
    DIRECTOR = "Director"


class WorkingTimeEnum(str, Enum):
    FULLTIME = "Fulltime"
    PARTTIME = "PartTime"


class SpecWorkingTimeEnum(str, Enum):
    REGULAR = "Regular"
    INTERRUPTIONS = "Interruptions"
    SEASONAL_WORKER = "SeasonalWorker"


class AgricultureTypeEnum(str, Enum):
    NONE = None
    HORTICULTURE = "Horticulture"
    HORTICULTURE_CHICORY = "HorticultureChicory"
    AGRICULTURE = "Agriculture"
    HORTICULTURE_MUSHROOM = "HorticultureMushroom"
    HORTICULTURE_FRUIT = "HorticultureFruit"


class UsingData(BaseModel):
    """Model for using data in contracts"""
    UsingJointCommissionNbr: Optional[str] = Field(None, min_length=3, max_length=3, pattern=r'^[0-9,.]*$')
    UsingEmployerName: Optional[str] = Field(None, min_length=0, max_length=40)
    UsingEmployerCompanyID: Optional[float] = Field(None, ge=0, le=9999999999)
    UsingStreet: Optional[str] = Field(None, min_length=0, max_length=100)
    UsingHouseNumber: Optional[str] = Field(None, min_length=0, max_length=10)
    UsingPostBox: Optional[str] = Field(None, min_length=0, max_length=5)
    UsingZIPCode: Optional[str] = Field(None, min_length=0, max_length=12)
    UsingCity: Optional[str] = Field(None, min_length=0, max_length=30)
    UsingCountry: Optional[str] = Field("00150", min_length=5, max_length=5, pattern=r'^[0-9]*$')


class CareerBreakDefinition(BaseModel):
    """Model for career break entries"""
    Exist: ResetEnum
    Kind: Optional[str] = Field(None, enum=[
        "Fulltime", "PartTimeOneFifth", "PartTimeOneQuarter", "PartTimeOneThird",
        "PartTimeHalf", "PartTimeThreeFifths", "PartTimeOneTenth"
    ])
    Reason: Optional[str] = Field(None, enum=[
        "PalliativeCare", "SeriouslyIll", "Other", "ParentalLeave", "Crisis",
        "FamilyCare", "EndOfCareer", "SickChild", "FamilyCareCorona",
        "ChildCareUnder8", "ChildCareHandicapUnder21", "CertifiedTraining"
    ])
    OriginallyContractType: Optional[WorkingTimeEnum] = None
    WeekhoursWorkerBefore: Optional[float] = None
    WeekhoursEmployerBefore: Optional[float] = None


class CertainWorkDefinition(BaseModel):
    """Model for certain work entries"""
    Exist: ResetEnum
    Description: Optional[str] = Field(None, min_length=0, max_length=250)


class ClsDimona(BaseModel):
    """Model for Dimona entries"""
    DimonaPeriodId: Optional[float] = Field(None, ge=0, le=999999999999)
    StartingDate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    EndingDate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    StartingHour: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$')
    EndingHour: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$')
    StartingHour2: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$')
    EndingHour2: Optional[str] = Field(None, min_length=12, max_length=12, pattern=r'^[0-9]*$')
    FirstMonthC32ANbr: Optional[float] = Field(None, ge=0, le=999999999999)
    NextMonthC32ANbr: Optional[float] = Field(None, ge=0, le=999999999999)
    PlannedHoursNbr: Optional[int] = Field(None, ge=0, le=999)
    UsingData: Optional[UsingData] = None
    Receipt: Optional[float] = Field(None, ge=0, le=999999999999)
    JointCommissionNbr: Optional[str] = Field(None, min_length=3, max_length=6, pattern=r'^[0-9,.]*$')
    WorkerType: Optional[str] = Field(None, min_length=3, max_length=3)
    LastAction: Optional[str] = Field(None, min_length=1, max_length=1)
    ExceedingHoursNbr: Optional[int] = Field(None, ge=0, le=999)
    QuotaExceeded: Optional[ResetEnum] = None
    Belated: Optional[ResetEnum] = None
    Status: Optional[str] = Field(None, enum=["Blocked", "InProgress", "OK", "Error"])
    Error: Optional[str] = None


class clsSalaryComposition(BaseModel):
    """Model for salary composition entries"""
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Code: int = Field(..., ge=1, le=8999)
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Days: Optional[int] = Field(None, ge=0, le=99)
    Hours: Optional[float] = Field(None, ge=0, le=9999)
    Unity: Optional[float] = None
    Percentage: Optional[float] = None
    Amount: Optional[float] = None
    Supplement: Optional[float] = None
    TypeOfIndexing: Optional[str] = Field(None, enum=[
        "NoIndexation", "Indexation", "FrozenSalary", "SalaryAboveScale"
    ])


class InternationalEmploymentDefinition(BaseModel):
    """Model for international employment entries"""
    Exist: ResetEnum
    Kind: Optional[str] = Field(None, enum=[
        "SecondmentFrom", "SalarySplit", "FrontierWorker", "SecondmentTo"
    ])
    BorderCountry: Optional[str] = Field("00111", min_length=5, max_length=5, pattern=r'^[0-9]*$')


class MethodOfRemunerationDefinition(BaseModel):
    """Model for remuneration method entries"""
    Exist: ResetEnum
    Remuneration: Optional[str] = Field(None, enum=["Commission", "Piece", "ServiceVouchers"])
    Payment: Optional[str] = Field(None, enum=["Fixed", "Variable", "Mixed"])


class ProgressiveWorkResumptionDefinition(BaseModel):
    """Model for progressive work resumption entries"""
    Exist: ResetEnum
    Risk: Optional[str] = Field(None, enum=["IncapacityForWork", "MaternityProtection"])
    Hours: Optional[int] = Field(None, ge=0, le=40)
    Minutes: Optional[int] = Field(None, ge=0, le=60)
    Days: Optional[float] = Field(None, ge=0, le=5)
    StartdateIllness: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Comment: Optional[str] = Field(None, min_length=0, max_length=200)


class ProtectedEmployeeDefinition(BaseModel):
    """Model for protected employee entries"""
    Exist: ResetEnum
    Reason: Optional[str] = Field(None, min_length=4, max_length=4, pattern=r'^[0-9]*$')
    Startdate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')


class RetiredDefinition(BaseModel):
    """Model for retired person entries"""
    Exist: ResetEnum
    Kind: Optional[str] = Field(None, enum=[
        "PensionPrivateSector", "SurvivalPension", "PensionSelfEmployed", "pensionPublicSector"
    ])
    DateRetired: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    ApplyCollecting2ndPensionPillar: Optional[ResetEnum] = None


class SportsPersonDefinition(BaseModel):
    """Model for sports person entries"""
    Exist: ResetEnum
    RecognizedForeignSportsperson: Optional[ResetEnum] = None
    OpportunityContract: Optional[ResetEnum] = None


class StudentDefinition(BaseModel):
    """Model for student entries"""
    Exist: ResetEnum
    SolidarityContribution: ResetEnum


class ContractModel(BaseModel):
    """Model for contract entries"""
    # Required fields
    Startdate: str = Field(..., min_length=8, max_length=8, pattern=r'^[0-9]*$')
    
    # Optional fields
    Enddate: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    EmploymentStatus: Optional[ContractTypeEnum] = None
    Contract: Optional[str] = Field(None, enum=[
        "Usually", "FlexiVerbal", "FlexiWritten", "FlexiLiable", "Sportsperson",
        "Housekeeper", "Servant", "Agriculture", "Homework", "HomeworkChildcare",
        "Physician", "PhysicianTraining", "PhysicianIndependant", "ApprenticeFlemisch",
        "ApprenticeFrench", "ApprenticeGerman", "ApprenticeManager", "ApprenticeIndustrial",
        "ApprenticeSocio", "ApprenticeBio", "ApprenticeAlternating", "EarlyRetirement",
        "EarlyRetirementPartTime", "FreeNOSS", "FreeNOSSManager", "FreeNOSSOther",
        "FreeNOSSSportingEvent", "FreeNOSSHelper", "FreeNOSSSocio", "FreeNOSSEducation",
        "FreeNOSSSpecialCultures", "FreeNOSSVolunteer", "Horeca", "HorecaExtraHourLiable",
        "HorecaExtraDayLiable", "HorecaExtraHourForfait", "HorecaExtraDayForfait",
        "HorecaFlexiVerbal", "HorecaFlexiWritten", "HorecaFlexiLiable", "Construction",
        "ConstructionAlternating", "ConstructionApprenticeYounger", "ConstructionApprentice",
        "ConstructionGodfather", "JobTrainingIBO", "JobTrainingSchool", "JobTrainingVDAB",
        "JobTrainingLiberalProfession", "JobTrainingEntry", "JobTrainingPFIWa",
        "JobTrainingABO", "JobTrainingPFIBx", "JobTrainingBIO", "JobTrainingAlternating",
        "JobTrainingDisability", "NonProfitRiziv", "NonProfitGesco", "NonProfitDAC",
        "NonProfitPrime", "NonProfitLowSkilled", "Artist", "ArtistWithContract",
        "ArtistWithoutContract", "Transport", "TransportNonMobile", "TransportGarage",
        "Aircrew", "AircrewPilot", "AircrewCabinCrew", "Interim", "InterimTemporary",
        "InterimsPermanent", "External", "ExternalApplicant", "ExternalSubcontractor",
        "ExternalAgentIndependant", "ExternalExtern", "ExternalIntern", "ExternalLegalPerson",
        "SalesRepresentative", "SportsTrainer"
    ])
    CatRSZ: Optional[str] = Field(None, min_length=3, max_length=3, pattern=r'^[0-9]*$')
    ParCom: Optional[str] = Field(None, min_length=3, max_length=10, pattern=r'^[0-9. ]*$')
    DocumentC78: Optional[str] = Field(None, enum=[
        "Nihil", "C783", "C784", "C78Activa", "C78Start", "C78Sine", "C78ShortTerm",
        "WalloniaLongtermJobSeekers", "WalloniaYoungJobSeekers", "WalloniaImpulsionInsertion",
        "BrusselsLongtermJobSeekers", "BrusselsReducedAbility"
    ])
    CodeC98: Optional[ResetEnum] = None
    CodeC131A: Optional[ResetEnum] = None
    CodeC131ARequestFT: Optional[ResetEnum] = None
    CodeC131: Optional[ResetEnum] = None
    Risk: Optional[str] = Field(None, min_length=0, max_length=10)
    SocialSecurityCard: Optional[str] = Field(None, min_length=0, max_length=15)
    WorkPermit: Optional[str] = Field(None, min_length=0, max_length=15)
    DateInService: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    Seniority: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    DateProfessionalExperience: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    ScaleSalarySeniority: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    StartProbationPeriod: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    EndProbationPeriod: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    FixedTerm: Optional[ResetEnum] = None
    EndFixedTerm: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    DateOutService: Optional[str] = Field(None, min_length=8, max_length=8, pattern=r'^[0-9]*$')
    ReasonOut: Optional[str] = None
    WorkingTime: Optional[WorkingTimeEnum] = None
    SpecWorkingTime: Optional[SpecWorkingTimeEnum] = None
    Schedule: Optional[str] = Field(None, min_length=0, max_length=4)
    WeekhoursWorker: Optional[float] = Field(None, ge=1, le=50)
    WeekhoursEmployer: Optional[float] = Field(None, ge=1, le=50)
    WeekhoursWorkerAverage: Optional[float] = Field(None, ge=1, le=50)
    WeekhoursEmployerAverage: Optional[float] = Field(None, ge=1, le=50)
    WeekhoursWorkerEffective: Optional[float] = Field(None, ge=1, le=50)
    WeekhoursEmployerEffective: Optional[float] = Field(None, ge=1, le=50)
    DaysWeek: Optional[float] = None
    DaysWeekFT: Optional[float] = None
    ReducingWorkingKind: Optional[str] = Field(None, enum=["Nihil", "Paid", "Unpaid"])
    ReducingWorkingKindDays: Optional[float] = None
    ReducingWorkingKindHours: Optional[float] = None
    PartTimeReturnTowork: Optional[str] = Field(None, min_length=0, max_length=4)
    ASRSchedule: Optional[str] = Field(None, min_length=0, max_length=2)
    ProffCat: Optional[str] = Field(None, min_length=0, max_length=10)
    Function: Optional[str] = Field(None, min_length=0, max_length=10)
    FunctionDescription: Optional[str] = Field(None, min_length=0, max_length=50)
    SocialBalanceJoblevel: Optional[str] = Field(None, enum=[
        "OperationalStaff", "ExecutiveStaff", "ManagementStaff", "ByFunction"
    ])
    Office: Optional[int] = None
    Division: Optional[str] = Field(None, min_length=0, max_length=10)
    InvoicingDivision: Optional[str] = Field(None, min_length=0, max_length=10)
    CostCentre: Optional[str] = Field(None, min_length=0, max_length=15)
    ScaleSalaryPrisma: Optional[ResetEnum] = None
    ScaleSalaryUse: Optional[ResetEnum] = None
    ScaleSalaryDefinition: Optional[str] = Field(None, min_length=0, max_length=10)
    ScaleSalaryCategory: Optional[str] = Field(None, min_length=0, max_length=10)
    ScaleSalaryScale: Optional[str] = Field(None, min_length=0, max_length=100)
    ExcludeForDMFAdeclaration: Optional[ResetEnum] = None
    AgricultureType: Optional[AgricultureTypeEnum] = None
    NoDimona: Optional[ResetEnum] = None
    NoDMFA: Optional[ResetEnum] = None
    NoASRDRS: Optional[ResetEnum] = None
    Security: Optional[str] = Field(None, min_length=0, max_length=10)
    
    # Nested models
    CareerBreak: Optional[CareerBreakDefinition] = None
    CertainWork: Optional[CertainWorkDefinition] = None
    Dimona: Optional[ClsDimona] = None
    InternationalEmployment: Optional[InternationalEmploymentDefinition] = None
    MethodOfRemuneration: Optional[MethodOfRemunerationDefinition] = None
    ProgressiveWorkResumption: Optional[ProgressiveWorkResumptionDefinition] = None
    ProtectedEmployee: Optional[ProtectedEmployeeDefinition] = None
    Retired: Optional[RetiredDefinition] = None
    Sportsperson: Optional[SportsPersonDefinition] = None
    Student: Optional[StudentDefinition] = None
    SalaryCompositions: Optional[List[clsSalaryComposition]] = None
