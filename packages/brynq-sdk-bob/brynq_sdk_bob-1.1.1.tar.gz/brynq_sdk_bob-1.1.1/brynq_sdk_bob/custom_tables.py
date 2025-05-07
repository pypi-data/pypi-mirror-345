from datetime import datetime
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.custom_tables import CustomTableSchema


class CustomTables:
    def __init__(self, bob):
        self.bob = bob

    def get(self, employee_id: str, custom_table_id: str) -> (pd.DataFrame, pd.DataFrame):
        """
        Get custom table data for an employee
        
        Args:
            employee_id: The employee ID
            custom_table_id: The custom table ID
            
        Returns:
            A tuple of (valid_data, invalid_data) as pandas DataFrames
        """
        resp = self.bob.session.get(url=f"{self.bob.base_url}people/custom-tables/{employee_id}/{custom_table_id}")
        resp.raise_for_status()
        data = resp.json()
        
        # Normalize the nested JSON response
        df = pd.json_normalize(
            data,
            record_path=['values']
        )
        
        df['employee_id'] = employee_id
        df = self.bob.rename_camel_columns_to_snake_case(df)
        valid_data, invalid_data = Functions.validate_data(df=df, schema=CustomTableSchema, debug=True)

        return valid_data, invalid_data 