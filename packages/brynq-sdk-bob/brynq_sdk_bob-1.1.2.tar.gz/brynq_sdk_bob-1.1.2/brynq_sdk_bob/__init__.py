import base64
import re
from typing import Union, List
import pandas as pd
import requests
from brynq_sdk_brynq import BrynQ
from .bank import Bank
from .company import Company
from .documents import CustomDocuments
from .employment import Employment
from .named_lists import NamedLists
from .payments import Payments
from .people import People
from .salaries import Salaries
from .timeoff import TimeOff
from .work import Work

class Bob(BrynQ):
    def __init__(self, label: Union[str, List], test_environment: bool = True, debug: bool = False, target_system: str = None):
        super().__init__()
        self.timeout = 3600
        self.headers = self._get_request_headers(label=label)
        if test_environment:
            self.base_url = "https://api.sandbox.hibob.com/v1/"
        else:
            self.base_url = "https://api.hibob.com/v1/"
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.people = People(self)
        self.salaries = Salaries(self)
        self.work = Work(self)
        self.bank = Bank(self)
        self.employment = Employment(self)
        self.payments = Payments(self)
        self.time_off = TimeOff(self)
        self.documents = CustomDocuments(self)
        self.companies = Company(self)
        self.named_lists = NamedLists(self)

    def _get_request_headers(self, label):
        credentials = self.get_system_credential(system='bob', label=label)
        auth_token = base64.b64encode(f"{credentials['User ID']}:{credentials['API Token']}".encode()).decode('utf-8')
        headers = {
            "accept": "application/json",
            "Authorization": f"Basic {auth_token}",
            "Partner-Token": "001Vg00000A6FY6IAN"
        }

        return headers

    def get_paginated_result(self, request: requests.Request) -> List:
        has_next_page = True
        result_data = []
        while has_next_page:
            prepped = request.prepare()
            prepped.headers.update(self.session.headers)
            resp = self.session.send(prepped, timeout=self.timeout)
            resp.raise_for_status()
            response_data = resp.json()
            result_data += response_data['results']
            next_cursor = response_data.get('response_metadata').get('next_cursor')
            # If there is no next page, set has_next_page to False, we could use the falsy value of None but this is more readable
            has_next_page = next_cursor is not None
            if has_next_page:
                request.params.update({"cursor": next_cursor})

        return result_data

    def rename_camel_columns_to_snake_case(self, df: pd.DataFrame) -> pd.DataFrame:
        def camel_to_snake_case(column):
            # Replace periods with underscores
            column = column.replace('.', '_')
            # Insert underscores before capital letters and convert to lowercase
            return re.sub(r'(?<!^)(?=[A-Z])', '_', column).lower()

        df.columns = map(camel_to_snake_case, df.columns)

        return df
