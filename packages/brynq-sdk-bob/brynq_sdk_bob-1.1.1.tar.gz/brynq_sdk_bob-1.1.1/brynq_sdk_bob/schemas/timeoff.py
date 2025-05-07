import pandera as pa
from pandera.typing import Series, String, Float
import pandas as pd

class TimeOffSchema(pa.DataFrameModel):
    change_type: Series[String] = pa.Field(coerce=True)
    employee_id: Series[String] = pa.Field(coerce=True)
    employee_display_name: Series[String] = pa.Field(coerce=True)
    employee_email: Series[String] = pa.Field(coerce=True)
    request_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    policy_type_display_name: Series[String] = pa.Field(coerce=True)
    type: Series[String] = pa.Field(coerce=True)
    start_date: Series[String] = pa.Field(coerce=True)
    start_portion: Series[String] = pa.Field(coerce=True)
    end_date: Series[String] = pa.Field(coerce=True)
    end_portion: Series[String] = pa.Field(coerce=True)
    day_portion: Series[String] = pa.Field(coerce=True)
    date: Series[String] = pa.Field(coerce=True)
    hours_on_date: Series[Float] = pa.Field(coerce=True)
    daily_hours: Series[Float] = pa.Field(coerce=True)
    duration_unit: Series[String] = pa.Field(coerce=True)
    total_duration: Series[Float] = pa.Field(coerce=True)
    total_cost: Series[Float] = pa.Field(coerce=True)
    change_reason: Series[String] = pa.Field(nullable=True, coerce=True)
    visibility: Series[String] = pa.Field(coerce=True)

    class Config:
        coerce = True