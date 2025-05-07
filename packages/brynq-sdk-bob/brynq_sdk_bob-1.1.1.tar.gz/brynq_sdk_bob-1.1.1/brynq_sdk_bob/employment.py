import pandas as pd
import requests
from .schemas.employment import EmploymentSchema
from brynq_sdk_functions import Functions


class Employment:
    def __init__(self, bob):
        self.bob = bob

    def get(self) -> (pd.DataFrame, pd.DataFrame):
        request = requests.Request(method='GET',
                                   url=f"{self.bob.base_url}bulk/people/employment")
        data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='values',
            meta=['employeeId']
        )
        df = self.bob.rename_camel_columns_to_snake_case(df)
        valid_contracts, invalid_contracts = Functions.validate_data(df=df, schema=EmploymentSchema, debug=True)

        return valid_contracts, invalid_contracts