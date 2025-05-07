import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.work import WorkSchema


class Work:
    def __init__(self, bob):
        self.bob = bob

    def get(self) ->(pd.DataFrame, pd.DataFrame):
        request = requests.Request(method='GET',
                                   url=f"{self.bob.base_url}bulk/people/work")
        data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='values',
            meta=['employeeId']
        )
        df = self.bob.rename_camel_columns_to_snake_case(df)

        valid_work, invalid_work = Functions.validate_data(df=df, schema=WorkSchema, debug=True)

        return valid_work, invalid_work