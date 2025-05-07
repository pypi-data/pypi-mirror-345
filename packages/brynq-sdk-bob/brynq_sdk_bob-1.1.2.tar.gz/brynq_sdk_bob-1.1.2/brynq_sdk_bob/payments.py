from datetime import datetime
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.payments import VariablePaymentSchema


class Payments:
    def __init__(self, bob):
        self.bob = bob

    def get(self, person_id: str) -> (pd.DataFrame, pd.DataFrame):
        resp = self.bob.session.get(url=f"{self.bob.base_url}people/{person_id}/variable", timeout=self.bob.timeout)
        resp.raise_for_status()
        data = resp.json()
        df = pd.json_normalize(
            data,
            record_path='values'
        )
        df['employee_id'] = person_id
        df = self.bob.rename_camel_columns_to_snake_case(df)
        valid_payments, invalid_payments = Functions.validate_data(df=df, schema=VariablePaymentSchema, debug=True)

        return valid_payments, invalid_payments
