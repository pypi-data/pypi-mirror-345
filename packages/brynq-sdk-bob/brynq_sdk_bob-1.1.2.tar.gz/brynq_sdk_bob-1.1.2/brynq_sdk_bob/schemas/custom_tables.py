import pandera as pa
from pandera.typing import Series
import pandas as pd

class CustomTableSchema(pa.DataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True)
    
    class Config:
        coerce = True 