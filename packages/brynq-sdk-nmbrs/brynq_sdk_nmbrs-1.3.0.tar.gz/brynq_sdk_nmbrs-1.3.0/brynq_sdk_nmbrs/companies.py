import pandas as pd
import requests
import logging
from .costcenter import Costcenter
from .costunit import Costunit
from .hours import Hours
from .bank import Bank
from .function import Functions
from zeep.exceptions import Fault
from zeep.helpers import serialize_object


class Companies:
    def __init__(self, nmbrs):
        self.nmbrs = nmbrs
        self.costcenters = Costcenter(nmbrs)
        self.costunits = Costunit(nmbrs)
        self.hours = Hours(nmbrs)
        self.banks = Bank(nmbrs)
        self.soap_client = nmbrs.soap_client
        self.logger = logging.getLogger(__name__)

    def get(self) -> pd.DataFrame:
        request = requests.Request(method='GET',
                                   url=f"{self.nmbrs.base_url}companies")
        data = self.nmbrs.get_paginated_result(request)
        return df

    def get_soap_ids(self) -> pd.DataFrame:
        """
        Get all companies using the SOAP API.
        
        Returns:
            pd.DataFrame: DataFrame containing all companies
        """
        try:
            # Get the auth header using the centralized method
            auth_header = self.nmbrs._get_soap_auth_header()

            # Make SOAP request with the proper header structure
            response = self.soap_client.service.List_GetAll(
                _soapheaders=[auth_header]
            )
            
            # Convert response to DataFrame
            if response:
                # Convert Zeep objects to Python dictionaries
                serialized_response = serialize_object(response)
                
                # Convert to DataFrame
                df = pd.DataFrame(serialized_response)
                
                return df
            else:
                return pd.DataFrame()

        except Fault as e:
            raise Exception(f"SOAP request failed: {str(e)}")
        except Exception as e:
            self.logger.exception("Exception occurred:")
            raise Exception(f"Failed to get companies: {str(e)}")
