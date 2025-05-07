from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import pandera as pa
from pandera import Bool, Int
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from pydantic import BaseModel, Field

# ---------------------------
# Get Schemas
# ---------------------------
class ScheduleGet(pa.DataFrameModel):
    schedule_id: Series[String] = pa.Field(coerce=True, description="Schedule ID", alias="scheduleId")
    start_date: Series[datetime] = pa.Field(coerce=True, description="Start Date", alias="startDate")
    parttime_percentage: Series[Float] = pa.Field(coerce=True, description="Part-Time Percentage", alias="parttimePercentage")
    week1_hours_monday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Monday", alias="week1HoursMonday")
    week1_hours_tuesday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Tuesday", alias="week1HoursTuesday")
    week1_hours_wednesday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Wednesday", alias="week1HoursWednesday")
    week1_hours_thursday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Thursday", alias="week1HoursThursday")
    week1_hours_friday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Friday", alias="week1HoursFriday")
    week1_hours_saturday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Saturday", alias="week1HoursSaturday")
    week1_hours_sunday: Series[Float] = pa.Field(coerce=True, description="Week 1 Hours Sunday", alias="week1HoursSunday")
    week2_hours_monday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Monday", alias="week2HoursMonday")
    week2_hours_tuesday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Tuesday", alias="week2HoursTuesday")
    week2_hours_wednesday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Wednesday", alias="week2HoursWednesday")
    week2_hours_thursday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Thursday", alias="week2HoursThursday")
    week2_hours_friday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Friday", alias="week2HoursFriday")
    week2_hours_saturday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Saturday", alias="week2HoursSaturday")
    week2_hours_sunday: Series[Float] = pa.Field(coerce=True, description="Week 2 Hours Sunday", alias="week2HoursSunday")
    created_at: Series[datetime] = pa.Field(coerce=True, description="Created At", alias="createdAt")

    class _Annotation:
        primary_key = "schedule_id"

# ---------------------------
# Upload Schemas
# ---------------------------
class ScheduleHours(BaseModel):
    """Schedule hours for each day of the week"""
    hours_monday: float = Field(..., description="Monday hours", alias="hoursMonday")
    hours_tuesday: float = Field(..., description="Tuesday hours", alias="hoursTuesday")
    hours_wednesday: float = Field(..., description="Wednesday hours", alias="hoursWednesday")
    hours_thursday: float = Field(..., description="Thursday hours", alias="hoursThursday")
    hours_friday: float = Field(..., description="Friday hours", alias="hoursFriday")
    hours_saturday: float = Field(..., description="Saturday hours", alias="hoursSaturday")
    hours_sunday: float = Field(..., description="Sunday hours", alias="hoursSunday")

class ScheduleCreate(BaseModel):
    """
    Pydantic model for creating a new schedule
    """
    start_date: datetime = Field(..., description="Start date of the schedule", example="2021-01-01T09:29:18Z", alias="startDate")
    hours_per_week: Optional[float] = Field(None, description="Hours per week", example=40, alias="hoursPerWeek")
    week1: ScheduleHours = Field(..., description="Week 1 schedule hours", alias="week1")
    week2: ScheduleHours = Field(..., description="Week 2 schedule hours", alias="week2")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "start_date": "2021-01-01T09:29:18Z",
                "hours_per_week": 40,
                "week1": {
                    "hours_monday": 8,
                    "hours_tuesday": 8,
                    "hours_wednesday": 8,
                    "hours_thursday": 8,
                    "hours_friday": 2.5,
                    "hours_saturday": 0,
                    "hours_sunday": 0
                },
                "week2": {
                    "hours_monday": 8,
                    "hours_tuesday": 8,
                    "hours_wednesday": 8,
                    "hours_thursday": 8,
                    "hours_friday": 2.5,
                    "hours_saturday": 0,
                    "hours_sunday": 0
                }
            }
        }

class ScheduleUpdate(BaseModel):
    """
    Pydantic model for updating a schedule
    """
    schedule_id: str = Field(..., example="e66ec3e9-6568-4fcf-9f45-945777a3e30d", description="Schedule ID", alias="scheduleId")
    start_date: datetime = Field(..., description="Start date of the schedule", example="2021-01-01T09:29:18Z", alias="startDate")
    hours_per_week: Optional[float] = Field(None, description="Hours per week", example=40, alias="hoursPerWeek")
    week1: ScheduleHours = Field(..., description="Week 1 schedule hours", alias="week1")
    week2: ScheduleHours = Field(..., description="Week 2 schedule hours", alias="week2")

    class Config:
        primary_key = "scheduleId"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScheduleDelete(BaseModel):
    schedule_id: str = Field(..., example="e66ec3e9-6568-4fcf-9f45-945777a3e30d", description="Schedule ID", alias="scheduleId")