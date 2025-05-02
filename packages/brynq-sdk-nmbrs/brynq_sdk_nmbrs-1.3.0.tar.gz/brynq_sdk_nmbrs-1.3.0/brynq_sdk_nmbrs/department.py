import math
import pandas as pd
import requests
from typing import Dict, Any
from .schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentDelete, Period, DepartmentGet
from brynq_sdk_functions import Functions


class EmployeeDepartment:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        departments = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            departments = pd.concat([departments, self._get(company, created_from, employee_id)])

        valid_departments, invalid_departments = Functions.validate_data(df=departments, schema=DepartmentGet, debug=True)

        return valid_departments, invalid_departments

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
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/departments",
                                   params=params)

        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='departments',
            meta=['employeeId']
        )

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new department for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing department data with fields matching
                 the DepartmentCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        department_model = DepartmentCreate(**data)

        if self.nmbrs.mock_mode:
            return department_model

        # Convert validated model to dict for API payload
        payload = department_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/department",
            json=payload
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update a department for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing department data with fields matching
                 the DepartmentUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        department_model = DepartmentUpdate(**data)

        if self.nmbrs.mock_mode:
            return department_model

        # Convert validated model to dict for API payload
        payload = department_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/department",
            json=payload
        )
        return resp

    def delete(self, employee_id: str, department_id: str):
        """
        Delete a department assignment for an employee.

        Args:
            employee_id: The ID of the employee
            department_id: The ID of the department to delete

        Returns:
            Response from the API
        """
        # Create and validate a DepartmentDelete model
        department_model = DepartmentDelete(departmentId=department_id)

        if self.nmbrs.mock_mode:
            return department_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/departments/{department_id}"
        )



class Departments:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            debtor_id: str) -> pd.DataFrame:
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}debtors/{debtor_id}/departments")

        data = self.nmbrs.get_paginated_result(request)
        df = pd.DataFrame(data)

        return df