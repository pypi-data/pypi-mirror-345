import pandas as pd
from brynq_sdk_functions import Functions
from .bank import Bank
from .employment import Employment
from .salaries import Salaries
from .schemas.people import PeopleSchema
from .work import Work
from .custom_tables import CustomTables


class People:
    def __init__(self, bob):
        self.bob = bob
        self.salaries = Salaries(bob)
        self.employment = Employment(bob)
        self.bank = Bank(bob)
        self.work = Work(bob)
        self.custom_tables = CustomTables(bob)

    def get(self) -> pd.DataFrame:
        resp = self.bob.session.get(url=f"{self.bob.base_url}profiles", timeout=self.bob.timeout)
        # Bob sucks with default fields so you need to do a search call to retrieve additional fields.
        additional_fields = [
            "personal.birthDate",
            "address.city",
            "address.postCode",
            "address.line1",
            "address.line2",
            "address.activeEffectiveDate",
            "address.country",
            # "home.legalGender",
            "home.spouse.firstName",
            "home.spouse.surname",
            # "home.spouse.birthDate",
            "home.spouse.gender",
            "internal.terminationReason",
            "internal.terminationDate",
            "internal.terminationType",
            "employee.lastDayOfWork",
            # housenumber addition
            "address.customColumns.column_1740046184782",
            # contract end date (bob only fills this when you get a new contract normally)
            "payroll.employment.customColumns.column_1680013460318",
            # iban
            "financial.iban"
            # ploegentoeslag
        ]
        resp_additional_fields = self.bob.session.post(url=f"{self.bob.base_url}people/search",
                                                       json={
                                                           "fields": ["root.id"] + additional_fields,
                                                           "filters": []
                                                       },
                                                       timeout=self.bob.timeout)
        df_extra_fields = pd.json_normalize(resp_additional_fields.json()['employees'])
        resp.raise_for_status()
        data = resp.json()
        df = pd.json_normalize(data['employees'])
        df = pd.merge(df, df_extra_fields[["id"] + additional_fields], left_on='id', right_on='id')
        df = self.bob.rename_camel_columns_to_snake_case(df)
        valid_people, invalid_people = Functions.validate_data(df=df, schema=PeopleSchema, debug=True)

        return valid_people, invalid_people
