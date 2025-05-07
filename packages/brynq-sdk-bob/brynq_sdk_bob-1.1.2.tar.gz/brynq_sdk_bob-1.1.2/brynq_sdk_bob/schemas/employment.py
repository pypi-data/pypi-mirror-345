import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime


class EmploymentSchema(pa.DataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    active_effective_date: Series[DateTime] = pa.Field(coerce=True)
    contract: Series[String] = pa.Field(coerce=True, nullable=True) # has a list of possible values
    creation_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    effective_date: Series[DateTime] = pa.Field(coerce=True)
    end_effective_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    fte: Series[Float] = pa.Field(coerce=True)
    is_current: Series[Bool] = pa.Field(coerce=True)
    modification_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    salary_pay_type: Series[String] = pa.Field(coerce=True, nullable=True)
    weekly_hours: Series[Float] = pa.Field(coerce=True, nullable=True)
    # weekly_hours_sort_factor: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False)
    actual_working_pattern_working_pattern_type: Series[pa.String] = pa.Field(nullable=True)
    actual_working_pattern_days_sunday: Series[Float] = pa.Field(nullable=True)
    actual_working_pattern_days_tuesday: Series[Float] = pa.Field(nullable=True)
    actual_working_pattern_days_wednesday: Series[Float] = pa.Field(nullable=True)
    actual_working_pattern_days_monday: Series[Float] = pa.Field(nullable=True)
    actual_working_pattern_days_friday: Series[Float] = pa.Field(nullable=True)
    actual_working_pattern_days_thursday: Series[Float] = pa.Field(nullable=True)
    actual_working_pattern_days_saturday: Series[Float] = pa.Field(nullable=True)