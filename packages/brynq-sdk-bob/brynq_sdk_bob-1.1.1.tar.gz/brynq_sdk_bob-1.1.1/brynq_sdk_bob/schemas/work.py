import pandera as pa
from pandera.typing import Series
import pandas as pd
from datetime import datetime

class WorkSchema(pa.DataFrameModel):
    can_be_deleted: Series[pa.Bool] = pa.Field(coerce=True)
    work_change_type: Series[str] = pa.Field(coerce=True)
    creation_date: Series[datetime] = pa.Field(coerce=True, nullable=True)
    title: Series[str] = pa.Field(coerce=True, nullable=True)
    is_current: Series[pa.Bool] = pa.Field(coerce=True)
    modification_date: Series[datetime] = pa.Field(coerce=True, nullable=True)
    site: Series[str] = pa.Field(coerce=True, nullable=True)
    site_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    end_effective_date: Series[datetime] = pa.Field(coerce=True, nullable=True)
    active_effective_date: Series[datetime] = pa.Field(coerce=True, nullable=True)
    department: Series[str] = pa.Field(coerce=True, nullable=True)
    effective_date: Series[datetime] = pa.Field(coerce=True, nullable=True)
    change_reason: Series[str] = pa.Field(coerce=True, nullable=True)
    change_changed_by: Series[str] = pa.Field(coerce=True, nullable=True)
    change_changed_by_id: Series[str] = pa.Field(coerce=True, nullable=True)
    reports_to_id: Series[str] = pa.Field(coerce=True, nullable=True)
    reports_to_first_name: Series[str] = pa.Field(coerce=True, nullable=True)
    reports_to_surname: Series[str] = pa.Field(coerce=True, nullable=True)
    reports_to_email: Series[str] = pa.Field(coerce=True, nullable=True)
    reports_to_display_name: Series[str] = pa.Field(coerce=True, nullable=True)
    reports_to: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True)
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
