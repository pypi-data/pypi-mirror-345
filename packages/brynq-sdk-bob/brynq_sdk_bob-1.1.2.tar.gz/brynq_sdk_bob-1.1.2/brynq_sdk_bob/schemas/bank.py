import pandera as pa
from pandera.typing import Series, String
import pandas as pd


class BankSchema(pa.DataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    amount: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    allocation: Series[String] = pa.Field(coerce=True, nullable=True)
    branch_address: Series[String] = pa.Field(coerce=True, nullable=True)
    bank_name: Series[String] = pa.Field(coerce=True, nullable=True)
    account_number: Series[String] = pa.Field(coerce=True, nullable=True)
    routing_number: Series[String] = pa.Field(coerce=True, nullable=True)
    bank_account_type: Series[String] = pa.Field(coerce=True, nullable=True)
    bic_or_swift: Series[String] = pa.Field(coerce=True, nullable=True)
    changed_by: Series[String] = pa.Field(coerce=True, nullable=True)
    iban: Series[String] = pa.Field(coerce=True)
    account_nickname: Series[String] = pa.Field(coerce=True, nullable=True)
    use_for_bonus: Series[pd.BooleanDtype] = pa.Field(coerce=True, nullable=True)
