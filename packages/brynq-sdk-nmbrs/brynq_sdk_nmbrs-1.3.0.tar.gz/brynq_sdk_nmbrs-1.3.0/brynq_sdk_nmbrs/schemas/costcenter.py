import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# ---------------------------
# Get Schemas
# ---------------------------
class EmployeeCostcenterGet(pa.DataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    employee_cost_center_id: Series[String] = pa.Field(coerce=True, description="Employee Cost Center ID", alias="employeeCostCenterId")
    cost_centers_cost_center_id: Series[String] = pa.Field(coerce=True, description="Cost Center ID", alias="costCentersCostCenterId")
    cost_centers_code: Series[String] = pa.Field(coerce=True, description="Cost Centers Code", alias="costCentersCode")
    cost_centers_description: Series[String] = pa.Field(coerce=True, description="Cost Centers Description", alias="costCentersDescription")
    cost_units_cost_unit_id: Series[String] = pa.Field(coerce=True, description="Cost Unit ID", alias="costUnitsCostUnitId")
    cost_units_code: Series[String] = pa.Field(coerce=True, description="Cost Unit Code", alias="costUnitsCode")
    cost_units_description: Series[String] = pa.Field(coerce=True, description="Cost Unit Description", alias="costUnitsDescription")
    percentage: Series[Float] = pa.Field(coerce=True, description="Percentage", alias="percentage")
    default: Series[Bool] = pa.Field(coerce=True, description="Default", alias="default")
    period_year: Series[int] = pa.Field(coerce=True, description="Year", alias="periodYear")
    period_period: Series[int] = pa.Field(coerce=True, description="Period", alias="periodPeriod")
    created_at: Series[DateTime] = pa.Field(coerce=True, description="Created At", alias="createdAt")

    class _Annotation:
        primary_key = "employee_cost_center_id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeeSchema",
                "parent_column": "employee_id",
                "cardinality": "N:1"
            }
        }

class CostcenterGet(pa.DataFrameModel):
    cost_center_id: Series[String] = pa.Field(coerce=True, description="Cost Center ID", alias="costCenterId")
    code: Series[String] = pa.Field(coerce=True, description="Code", alias="code")
    description: Series[String] = pa.Field(coerce=True, description="Description", alias="description")

    class _Annotation:
        primary_key = "cost_center_id"

# ---------------------------
# Upload Schemas
# ---------------------------
class EmployeeCostcenterCreate(BaseModel):
    employee_id: str = Field(..., example="0c59c3e4-ee35-42ec-bd00-75510a12ecad", description="Employee ID", alias="employeeId")
    cost_center_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="b505f980-1c4c-42c1-8ddb-2d90c58da0b2", description="Cost Unit ID", alias="costUnitId")
    percentage: float = Field(100, example=100, description="Percentage", alias="percentage")
    default: bool = Field(True, example=True, description="Default", alias="default")
    period_year: int = Field(..., example=2023, description="Year", alias="periodYear")
    period_period: int = Field(..., example=12, description="Period", alias="periodPeriod")

class EmployeeCostcenterUpdate(BaseModel):
    employee_cost_center_id: str = Field(..., example="c605f980-1c4c-42c1-8ddb-2d90c58da0b3", description="Employee Cost Center ID", alias="employeeCostCenterId")
    cost_center_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")
    cost_unit_id: Optional[str] = Field(None, example="b505f980-1c4c-42c1-8ddb-2d90c58da0b2", description="Cost Unit ID", alias="costUnitId")
    percentage: float = Field(100, example=100, description="Percentage", alias="percentage")
    default: bool = Field(True, example=True, description="Default", alias="default")

    class Config:
        primary_key = "employeeCostCenterId"

class EmployeeCostcenterDelete(BaseModel):
    employee_cost_center_id: str = Field(..., example="c605f980-1c4c-42c1-8ddb-2d90c58da0b3", description="Employee Cost Center ID", alias="employeeCostCenterId")

# CostCenter CRUD schemas - These are hypothetical since the API doesn't have create/update/delete endpoints
# but we add them for consistency with other schema files
class CostcenterCreate(BaseModel):
    code: str = Field(..., example="CC001", description="Code", alias="code")
    description: str = Field(..., example="Sales Department", description="Description", alias="description")

class CostcenterUpdate(BaseModel):
    cost_center_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")
    code: str = Field(..., example="CC001", description="Code", alias="code")
    description: str = Field(..., example="Sales Department", description="Description", alias="description")

    class Config:
        primary_key = "costCenterId"

class CostcenterDelete(BaseModel):
    cost_center_id: str = Field(..., example="a405f980-1c4c-42c1-8ddb-2d90c58da0b1", description="Cost Center ID", alias="costCenterId")