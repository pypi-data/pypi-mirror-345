import pandera as pa
from pandera.typing import Series

class NamedListSchema(pa.DataFrameModel):
    id: Series[str] = pa.Field(coerce=True)
    value: Series[str] = pa.Field(coerce=True)
    name: Series[str] = pa.Field(coerce=True)
    archived: Series[bool] = pa.Field(coerce=True)
    # children: Series[list] = pa.Field(coerce=True)
    type: Series[str] = pa.Field(coerce=True)

    class Config:
        coerce = True 