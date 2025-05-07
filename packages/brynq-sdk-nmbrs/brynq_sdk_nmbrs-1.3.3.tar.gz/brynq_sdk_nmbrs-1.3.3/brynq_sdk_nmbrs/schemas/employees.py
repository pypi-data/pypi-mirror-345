import math
import pandas as pd
import pandera as pa
from pandera.typing import Series, String, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

# ---------------------------
# Get Schemas
# ---------------------------
class EmployeeGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    personal_info_id: Series[String] = pa.Field(coerce=True, description="Personal Info ID", alias="personalInfoId")
    created_at: Series[DateTime] = pa.Field(coerce=True, description="Employee Created At", alias="createdAt")
    basic_info_employee_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee Number", alias="employeeNumber")
    basic_info_first_name: Series[String] = pa.Field(coerce=True, nullable=True, description="First Name", alias="firstName")
    basic_info_first_name_in_full: Series[String] = pa.Field(coerce=True, nullable=True, description="First Name In Full", alias="firstNameInFull")
    basic_info_prefix: Series[String] = pa.Field(coerce=True, nullable=True, description="Prefix", alias="prefix")
    basic_info_initials: Series[String] = pa.Field(coerce=True, nullable=True, description="Initials", alias="initials")
    basic_info_last_name: Series[String] = pa.Field(coerce=True, description="Last Name", alias="lastName")
    basic_info_employee_type: Series[String] = pa.Field(coerce=True, description="Employee Type", alias="employeeType")
    birth_info_birth_date: Series[DateTime] = pa.Field(coerce=True, description="Birth Date", alias="birthDate")
    birth_info_birth_country_code_i_s_o: Series[String] = pa.Field(coerce=True, nullable=True, description="Birth Country Code ISO", alias="birthCountryCodeISO")
    birth_info_nationality_code_i_s_o: Series[String] = pa.Field(coerce=True, nullable=True, description="Nationality Code ISO", alias="nationalityCodeISO")
    birth_info_gender: Series[String] = pa.Field(coerce=True, nullable=True, description="Gender", alias="gender")
    contact_info_private_email: Series[String] = pa.Field(coerce=True, nullable=True, description="Private Email", alias="privateEmail")
    contact_info_business_email: Series[String] = pa.Field(coerce=True, nullable=True, description="Business Email", alias="businessEmail")
    contact_info_business_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Business Phone", alias="businessPhone")
    contact_info_business_mobile_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Business Mobile Phone", alias="businessMobilePhone")
    contact_info_private_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Private Phone", alias="privatePhone")
    contact_info_private_mobile_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Private Mobile Phone", alias="privateMobilePhone")
    contact_info_other_phone: Series[String] = pa.Field(coerce=True, nullable=True, description="Other Phone", alias="otherPhone")
    partner_info_partner_prefix: Series[String] = pa.Field(coerce=True, nullable=True, description="Partner Prefix", alias="partnerPrefix")
    partner_info_partner_name: Series[String] = pa.Field(coerce=True, nullable=True, description="Partner Name", alias="partnerName")
    period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year", alias="periodYear")
    period_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period", alias="periodPeriod")
    birth_info_birth_country: Series[String] = pa.Field(coerce=True, nullable=True, description="Birth Country", alias="birthCountry")
    company_id: Series[String] = pa.Field(coerce=True, description="Company ID", alias="companyId")

    class _Annotation:
        primary_key = "employee_id"

# ---------------------------
# Upload Schemas
# ---------------------------
class BasicInfo(BaseModel):
    employee_number: Optional[int] = Field(None, ge=1, example=98072, description="Employee Number", alias="employeeNumber")
    first_name: Optional[str] = Field(None, max_length=50, example="John", description="First Name", alias="firstName")
    first_name_in_full: Optional[str] = Field(None, max_length=100, example="John in Full", description="First Name In Full", alias="firstNameInFull")
    prefix: Optional[str] = Field(None, max_length=50, example="van der", description="Prefix", alias="prefix")
    initials: Optional[str] = Field(None, max_length=50, example="J.D.", description="Initials", alias="initials")
    last_name: str = Field(..., max_length=100, example="Doe", description="Last Name", alias="lastName")
    employee_type: Annotated[
        str, 
        StringConstraints(
            pattern=r'^(applicant|newHire|payroll|formerPayroll|external|formerExternal|rejectedApplicant)$',
            strip_whitespace=True
        )
    ] = Field(..., example="payroll", description="Employee Type", alias="employeeType")

class BirthInfo(BaseModel):
    birth_date: Optional[str] = Field(None, example="1980-02-27", description="Birth Date", alias="birthDate")
    birth_country_code_iso: Optional[Annotated[
        str, 
        StringConstraints(
            pattern=r'^[A-Za-z]+$',
            strip_whitespace=True,
            min_length=2, 
            max_length=3
        )
    ]] = Field(None, example="NL", description="Birth Country Code ISO", alias="birthCountryCodeISO")
    nationality_code_iso: Optional[Annotated[
        str, 
        StringConstraints(
            pattern=r'^[A-Za-z]+$',
            strip_whitespace=True,
            min_length=2, 
            max_length=3
        )
    ]] = Field(None, example="PT", description="Nationality Code ISO", alias="nationalityCodeISO")
    deceased_on: Optional[str] = Field(None, example="1980-02-27", description="Deceased On", alias="deceasedOn")
    gender: Optional[Annotated[
        str, 
        StringConstraints(
            pattern=r'^(unspecified|male|female|unknown)$',
            strip_whitespace=True
        )
    ]] = Field(None, example="male", description="Gender", alias="gender")

class ContactInfo(BaseModel):
    private_email: Optional[str] = Field(None, max_length=100, example="doe@private.com", description="Private Email", alias="privateEmail")
    business_email: Optional[str] = Field(None, max_length=100, example="doe@business.com", description="Business Email", alias="businessEmail")
    business_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Business Phone", alias="businessPhone")
    business_mobile_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Business Mobile Phone", alias="businessMobilePhone")
    private_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Private Phone", alias="privatePhone")
    private_mobile_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Private Mobile Phone", alias="privateMobilePhone")
    other_phone: Optional[str] = Field(None, max_length=50, example="+351222222", description="Other Phone", alias="otherPhone")

class PartnerInfo(BaseModel):
    partner_prefix: Optional[str] = Field(None, max_length=50, example="Mstr", description="Partner Prefix", alias="partnerPrefix")
    partner_name: Optional[str] = Field(None, max_length=100, example="Jane Doe", description="Partner Name", alias="partnerName")
    ascription_code: Optional[int] = Field(None, ge=0, example=0, description="Ascription Code", alias="ascriptionCode")

class Period(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")

class AdditionalEmployeeInfo(BaseModel):
    in_service_date: str = Field(..., example="2019-08-24", description="In Service Date", alias="inServiceDate")
    default_employee_template: Optional[str] = Field(None, description="Default Employee Template", alias="defaultEmployeeTemplate")

class CreateEmployeePersonalInfo(BaseModel):
    basic_info: BasicInfo
    birth_info: BirthInfo
    contact_info: ContactInfo
    partner_info: PartnerInfo
    period: Period
    created_at: Optional[str] = Field(None, example="2021-07-01T10:15:08Z", description="Created At", alias="createdAt")

class EmployeeCreate(BaseModel):
    personal_info: CreateEmployeePersonalInfo
    additional_employee_info: AdditionalEmployeeInfo

class UpdateEmployeePersonalInfo(BaseModel):
    basic_info: Optional[BasicInfo] = None
    birth_info: Optional[BirthInfo] = None
    contact_info: Optional[ContactInfo] = None
    partner_info: Optional[PartnerInfo] = None
    period: Period

class EmployeeUpdate(BaseModel):
    employee_id: str = Field(..., example="d30ec597-bd29-453e-9613-7786297eedcc", description="Employee ID", alias="employeeId")
    personal_info: UpdateEmployeePersonalInfo

class EmployeeDelete(BaseModel):
    employee_id: str = Field(..., example="3054d4cf-b449-489d-8d2e-5dd30e5ab994", description="Employee ID", alias="employeeId")