import pandera as pa
from pandera.typing import Series, String, Float, DateTime
import pandas as pd

class VariablePaymentSchema(pa.DataFrameModel):
    can_be_deleted: Series[bool] = pa.Field(nullable=True, coerce=True)
    department_percent: Series[Float] = pa.Field(nullable=True, coerce=True)
    payout_type: Series[String] = pa.Field(coerce=True)
    num_of_salaries: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True)
    end_date: Series[DateTime] = pa.Field(nullable=True, coerce=True)
    creation_date: Series[DateTime] = pa.Field(coerce=True)
    percentage_of_annual_salary: Series[Float] = pa.Field(nullable=True, coerce=True)
    individual_percent: Series[Float] = pa.Field(nullable=True, coerce=True)
    variable_type: Series[String] = pa.Field(nullable=True, coerce=True)
    is_current: Series[bool] = pa.Field(nullable=True, coerce=True)
    modification_date: Series[DateTime] = pa.Field(nullable=True, coerce=True)
    company_percent: Series[Float] = pa.Field(nullable=True, coerce=True)
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    end_effective_date: Series[DateTime] = pa.Field(nullable=True, coerce=True)
    payment_period: Series[String] = pa.Field(coerce=True)
    effective_date: Series[DateTime] = pa.Field(coerce=True)
    amount_value: Series[Float] = pa.Field(coerce=True)
    amount_currency: Series[String] = pa.Field(coerce=True)
    change_reason: Series[String] = pa.Field(nullable=True, coerce=True)
    change_changed_by: Series[String] = pa.Field(nullable=True, coerce=True)
    change_changed_by_id: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True)
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)

    class Config:
        coerce = True