import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions


class SalarySchema(pa.DataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    pay_frequency: Series[String] = pa.Field(coerce=True, nullable=True) # has a list of possible values , isin=['Monthly']
    creation_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    is_current: Series[Bool] = pa.Field(coerce=True)
    modification_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    effective_date: Series[DateTime] = pa.Field(coerce=True)
    end_effective_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    change_reason: Series[str] = pa.Field(coerce=True, nullable=True)
    pay_period: Series[String] = pa.Field(coerce=True, nullable=True)
    base_value: Series[Float] = pa.Field(coerce=True, nullable=True)
    base_currency: Series[String] = pa.Field(coerce=True, isin=['EUR', 'USD'])
    active_effective_date: Series[DateTime] = pa.Field(coerce=True)
