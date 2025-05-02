import pandas as pd
import requests
from .costcenter import Costcenter, Costunit
from .department import Departments
from .hours import Hours
from .bank import Bank
from .function import Functions


class Debtors:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.departments = Departments(nmbrs)
        self.functions = Functions(nmbrs)


    def get(self) -> pd.DataFrame:
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}debtors")
        data = self.nmbrs.get_paginated_result(request)

        return df
