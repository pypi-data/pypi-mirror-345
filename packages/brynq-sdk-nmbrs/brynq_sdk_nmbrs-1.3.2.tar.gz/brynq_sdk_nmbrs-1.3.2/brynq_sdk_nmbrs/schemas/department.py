from datetime import datetime
import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional
from pydantic import BaseModel, Field

# ---------------------------
# Get Schemas
# ---------------------------
class DepartmentGet(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    department_id: Series[String] = pa.Field(coerce=True, description="Department ID", alias="departmentId")
    code: Series[String] = pa.Field(coerce=True, description="Department Code", alias="code")
    description: Series[String] = pa.Field(coerce=True, description="Department Description", alias="description")
    created_at: Series[DateTime] = pa.Field(coerce=True, description="Created At", alias="createdAt")
    period_period: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Period", alias="periodPeriod")
    period_year: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Year", alias="periodYear")

    class _Annotation:
        primary_key = "department_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

# ---------------------------
# Upload Schemas
# ---------------------------
class Period(BaseModel):
    year: int = Field(..., ge=1900, le=2100, example=2021, description="Year", alias="year")
    period: int = Field(..., ge=1, le=53, example=4, description="Period", alias="period")

class DepartmentCreate(BaseModel):
    code: int = Field(..., ge=1, example=2, description="Department Code", alias="code")
    description: str = Field(..., min_length=1, max_length=200, example="Sales", description="Department Description", alias="description")

class DepartmentUpdate(BaseModel):
    department_id: str = Field(..., example="3214", description="Department ID", alias="departmentId")
    period_details: Period

    class Config:
        primary_key = "departmentId"

class DepartmentDelete(BaseModel):
    department_id: str = Field(..., example="3214", description="Department ID", alias="departmentId")