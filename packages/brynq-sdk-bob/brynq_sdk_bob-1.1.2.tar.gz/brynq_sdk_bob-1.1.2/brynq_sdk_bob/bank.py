import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.bank import BankSchema


class Bank:
    def __init__(self, bob):
        self.bob = bob

    def get(self, person_ids: pd.Series) -> (pd.DataFrame, pd.DataFrame):
        data = []
        for person_id in person_ids:
            resp = self.bob.session.get(url=f"{self.bob.base_url}people/{person_id}/bank-accounts", timeout=self.bob.timeout)
            resp.raise_for_status()
            temp_data = resp.json()['values']
            # when an employee has one or more bank accounts, the response is a list of dictionaries.
            for account in temp_data:
                account['employee_id'] = person_id
            data += temp_data

        df = pd.DataFrame(data)
        df = self.bob.rename_camel_columns_to_snake_case(df)

        valid_banks, invalid_banks = Functions.validate_data(df=df, schema=BankSchema, debug=True)

        return valid_banks, invalid_banks