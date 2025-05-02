import pandas as pd
import requests
from brynq_sdk_functions import Functions as BrynQFunctions
import math
from typing import Dict, Any
from .schemas.function import FunctionGet, FunctionCreate, FunctionUpdate, FunctionDelete


class EmployeeFunction:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        functions = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            functions = pd.concat([functions, self._get(company, created_from)])

        valid_functions, invalid_functions = BrynQFunctions.validate_data(df=functions, schema=FunctionGet, debug=True)

        return valid_functions, invalid_functions

    def _get(self,
            company_id: str,
            created_from: str = None) -> pd.DataFrame:
        params = {}
        if created_from:
            params['createdFrom'] = created_from
        try:
            request = requests.Request(method='GET', url=f"{self.nmbrs.base_url}companies/{company_id}/employees/functions", params=params)
            data = self.nmbrs.get_paginated_result(request)
            df = pd.json_normalize(
                data,
                record_path='functions',
                meta=['employeeId']
            )
        except requests.HTTPError as e:
            df = pd.DataFrame()
        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new function for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing function data with fields matching
                 the FunctionCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        function_model = FunctionCreate(**data)

        if self.nmbrs.mock_mode:
            return function_model

        # Convert validated model to dict for API payload
        payload = function_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/function",
            json=payload
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update a function for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing function data with fields matching
                 the FunctionUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model
        function_model = FunctionUpdate(**data)

        if self.nmbrs.mock_mode:
            return function_model

        # Convert validated model to dict for API payload
        payload = function_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/function",
            json=payload
        )
        return resp

    def delete(self, employee_id: str, function_id: str):
        """
        Delete a function for an employee.

        Args:
            employee_id: The ID of the employee
            function_id: The ID of the function to delete

        Returns:
            Response from the API
        """
        # Create and validate a FunctionDelete model
        function_model = FunctionDelete(functionId=function_id)

        if self.nmbrs.mock_mode:
            return function_model

        # Send request
        resp = self.nmbrs.session.delete(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/functions/{function_id}"
        )
        return resp


class Functions:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self, debtor_id: str) -> pd.DataFrame:
        try:
            request = requests.Request(method='GET',
                                       url=f"{self.nmbrs.base_url}debtors/{debtor_id}/functions")

            data = self.nmbrs.get_paginated_result(request)
            df = pd.DataFrame(data)
        except requests.HTTPError as e:
            df = pd.DataFrame()

        return df