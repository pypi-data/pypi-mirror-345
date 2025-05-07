import pandas as pd
import requests
from dateutil.utils import today
from requests import HTTPError
from typing import Dict, Any

from brynq_sdk_functions import Functions
from .schemas.costcenter import CostcenterGet, EmployeeCostcenterGet
from .schemas.costcenter import EmployeeCostcenterCreate, EmployeeCostcenterUpdate, EmployeeCostcenterDelete
from .schemas.costcenter import CostcenterCreate, CostcenterUpdate, CostcenterDelete


class EmployeeCostcenter:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self,
            created_from: str = None,
            employee_id: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        costcenters = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            costcenters = pd.concat([costcenters, self._get(company, created_from, employee_id)])

        valid_costcenters, invalid_costcenters = Functions.validate_data(df=costcenters, schema=EmployeeCostcenterGet, debug=True)

        return valid_costcenters, invalid_costcenters

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
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/employees/costcenters",
                                   params=params)
        data = self.nmbrs.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='employeeCostCenters',
            meta=['employeeId']
        )

        return df

    def create(self, employee_id: str, data: Dict[str, Any]):
        """
        Create a new costcenter for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing costcenter data with fields matching
                 the EmployeeCostcenterCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        costcenter_model = EmployeeCostcenterCreate(**data)

        if self.nmbrs.mock_mode:
            return costcenter_model

        # Convert validated model to dict for API payload
        payload = costcenter_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/costcenter",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, employee_id: str, data: Dict[str, Any]):
        """
        Update a costcenter for an employee using Pydantic validation.

        Args:
            employee_id: The ID of the employee
            data: Dictionary containing costcenter data with fields matching
                 the EmployeeCostcenterUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        costcenter_model = EmployeeCostcenterUpdate(**data)

        if self.nmbrs.mock_mode:
            return costcenter_model

        # Convert validated model to dict for API payload
        payload = costcenter_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}employees/{employee_id}/costcenter",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp



class Costcenter:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs

    def get(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        costcenters = pd.DataFrame()
        for company in self.nmbrs.company_ids:
            costcenters = pd.concat([costcenters, self._get(company)])

        valid_costcenters, invalid_costcenters = Functions.validate_data(df=costcenters, schema=CostcenterGet, debug=True)

        return valid_costcenters, invalid_costcenters

    def _get(self,
            company_id: str):
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies/{company_id}/costcenters")
        data = self.nmbrs.get_paginated_result(request)
        df = pd.DataFrame(data)

        return df

    def create(self, company_id: str, data: Dict[str, Any]):
        """
        Create a new costcenter using Pydantic validation.

        Args:
            company_id: The ID of the company
            data: Dictionary containing costcenter data with fields matching
                 the CostcenterCreate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        costcenter_model = CostcenterCreate(**data)

        if self.nmbrs.mock_mode:
            return costcenter_model

        # Convert validated model to dict for API payload
        payload = costcenter_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.post(
            url=f"{self.nmbrs.base_url}companies/{company_id}/costcenter",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp

    def update(self, company_id: str, data: Dict[str, Any]):
        """
        Update a costcenter using Pydantic validation.

        Args:
            company_id: The ID of the company
            data: Dictionary containing costcenter data with fields matching
                 the CostcenterUpdate schema (using camelCase field names)

        Returns:
            Response from the API
        """
        # Validate with Pydantic model - this will raise an error if required fields are missing
        costcenter_model = CostcenterUpdate(**data)

        if self.nmbrs.mock_mode:
            return costcenter_model

        # Convert validated model to dict for API payload
        payload = costcenter_model.dict(exclude_none=True)

        # Send request
        resp = self.nmbrs.session.put(
            url=f"{self.nmbrs.base_url}companies/{company_id}/costcenter",
            json=payload,
            timeout=self.nmbrs.timeout
        )
        return resp
