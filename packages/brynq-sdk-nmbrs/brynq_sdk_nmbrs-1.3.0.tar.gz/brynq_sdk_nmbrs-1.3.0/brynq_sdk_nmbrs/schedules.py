import pandas as pd
import requests
import math
from brynq_sdk_functions import Functions
from .schemas.schedules import ScheduleGet, ScheduleCreate, ScheduleUpdate, ScheduleDelete, ScheduleHours
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class Schedule:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        schedules = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            schedules = pd.concat([schedules, self._get(company, created_from, employee_id)])

        valid_schedules, invalid_schedules = Functions.validate_data(df=schedules, schema=ScheduleGet, debug=True)

        return valid_schedules, invalid_schedules

    def _get(self,
            company_id: str,
            created_from: str = None,
            employee_id: str = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        if employee_id:
            params['employeeId'] = employee_id

        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/schedules",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='schedules',
            meta=['employeeId']
        )
        return df

    def create(self,
               employee_id: str,
               data: Dict[str, Any]):
        """
        Create a new schedule for an employee using Pydantic validation
        
        Args:
            employee_id: The employee ID
            data: Schedule data dictionary with the following keys:
                - start_date_schedule: Start date of the schedule
                - weekly_hours: Hours per week (optional)
                - hours_monday, hours_tuesday, etc.: Hours for each day
                
        Returns:
            Response from the API
        """
        # Transform data to match schema
        schedule_data = {}
        
        # Required field
        if "start_date_schedule" in data:
            schedule_data["startDate"] = data["start_date_schedule"]
        
        # Optional field
        if "weekly_hours" in data:
            # Handle NaN values
            if not isinstance(data["weekly_hours"], float) or not math.isnan(data["weekly_hours"]):
                schedule_data["hoursPerWeek"] = data["weekly_hours"]
        
        # Create week1 and week2 data
        week1_data = {}
        week2_data = {}
        
        day_mapping = {
            "hours_monday": "hoursMonday",
            "hours_tuesday": "hoursTuesday",
            "hours_wednesday": "hoursWednesday",
            "hours_thursday": "hoursThursday",
            "hours_friday": "hoursFriday",
            "hours_saturday": "hoursSaturday",
            "hours_sunday": "hoursSunday"
        }
        
        # Populate week1 data
        for day, api_day in day_mapping.items():
            if day in data and (not isinstance(data[day], float) or not math.isnan(data[day])):
                week1_data[api_day] = data[day]
            else:
                # Default to 0 hours if not specified
                week1_data[api_day] = 0.0
        
        # For now, set week2 same as week1 (can be adjusted if needed)
        week2_data = week1_data.copy()
        
        schedule_data["week1"] = week1_data
        schedule_data["week2"] = week2_data
        
        # Validate with Pydantic schema
        try:
            validated_data = ScheduleCreate(**schedule_data)
            
            if self.nmbrs.mock_mode:
                return validated_data
            
            # Use the validated data for the API call
            resp = self.nmbrs.session.post(
                url=f"{self.nmbrs.base_url}employees/{employee_id}/schedule",
                json=validated_data.dict(exclude_none=True)
            )
            return resp
            
        except Exception as e:
            raise ValueError(f"Schedule validation failed: {str(e)}")

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update a schedule for an employee using Pydantic validation.
        
        Args:
            employee_id: The ID of the employee
            data: Dictionary containing schedule data with fields matching
                 the ScheduleUpdate schema (using camelCase field names)
            
        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        schedule_model = ScheduleUpdate(**data)
        
        if self.nmbrs.mock_mode:
            return schedule_model
        
        # Convert validated model to dict for API payload
        payload = schedule_model.dict(exclude_none=True)
        
        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/schedule",
            json=payload
        )
        return resp
        
    def delete(self, employee_id: str, schedule_id: str):
        """
        Delete a schedule for an employee.
        
        Args:
            employee_id: The ID of the employee
            schedule_id: The ID of the schedule to delete
            
        Returns:
            Response from the API
        """
        # Create and validate a ScheduleDelete model
        schedule_model = ScheduleDelete(scheduleId=schedule_id)
        
        if self.nmbrs.mock_mode:
            return schedule_model
            
        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/schedules/{schedule_id}"
        )
        return resp
