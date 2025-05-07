from datetime import datetime, timezone
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.timeoff import TimeOffSchema


class TimeOff:
    def __init__(self, bob):
        self.bob = bob

    def get(self, since: datetime) -> (pd.DataFrame, pd.DataFrame):
        resp = self.bob.session.get(url=f"{self.bob.base_url}timeoff/requests/changes",
                                    params={'since': since.replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds')},
                                    timeout=self.bob.timeout)
        resp.raise_for_status()
        data = resp.json()['changes']
        # data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='changes',
            meta=['employeeId']
        )
        df = self.bob.rename_camel_columns_to_snake_case(df)
        valid_timeoff, invalid_timeoff = Functions.validate_data(df=df, schema=TimeOffSchema, debug=True)

        return valid_timeoff, invalid_timeoff