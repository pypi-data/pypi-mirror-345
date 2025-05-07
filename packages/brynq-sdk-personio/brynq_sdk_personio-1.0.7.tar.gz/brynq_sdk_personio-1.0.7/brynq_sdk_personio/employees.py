import requests
import pandas as pd


class Employees:

    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url

    def get(self, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """
        This endpoint gives all the data for all the employees. The absence_entitlement and holiday_calendar is removed since those attributes
        can have multiple lines per employee. Call get_absence_entitlements and get_holiday_calendar to get those attributes. Since we cannot exclude
        attributes in the request, we remove them afterwards.
        :param limit: Pagination attribute to limit the number of employees returned per page. Default is 100.
        :param offset: Pagination attribute to identify the first item in the collection to return. Default is 0.
        :return: A pandas DataFrame containing the fetched employees.
        """
        url = f'{self.base_url}company/employees?limit={limit}&offset={offset}'
        df = pd.DataFrame()
        while True:
            response = requests.get(url, headers=self.headers, timeout=3600)
            response.raise_for_status()
            df_temp = pd.json_normalize(response.json()['data'])
            df = pd.concat([df, df_temp])
            total_pages = response.json()['metadata']['total_pages']
            if offset < total_pages:
                offset += limit
                url = f'{self.base_url}company/employees?limit={limit}&offset={offset}'
            else:
                break

        # drop each column which ends with .label, .type and .universal_id
        df = df.drop(df.filter(regex='\.label$|\.type$|\.universal_id$').columns, axis=1)

        # Drop each column which starts with absence_entitlements or holiday_calendar. Since we can only include
        # attributes in the request but not exclude them, we remove them afterwards
        df = df.drop(df.filter(regex='^attributes\.absence_entitlement|^attributes\.holiday_calendar').columns, axis=1)

        # these column contain nested dicts, so their value is empty when json_normalized.
        df = df.drop(columns=['attributes.team.value',
                              'attributes.subcompany.value',
                              'attributes.department.value',
                              'attributes.office.value',
                              'attributes.team.value'])

        # From the supervisor data, only keep the id column and remove all the others. rename the column to supervisor_id
        supervisor_cols = df.filter(regex='^attributes\.supervisor').columns
        for column in supervisor_cols:
            if column.endswith('.id.value'):
                df[column] = df[column].fillna(0)
                df.rename(columns={column: 'supervisor_id'}, inplace=True)
            else:
                df.drop(column, axis=1, inplace=True)

        # Each column starts with attributes. we need to remove it
        df.columns = df.columns.str.replace('attributes.', '')
        df.columns = df.columns.str.replace('.value.id', '_id')
        df.columns = df.columns.str.replace('.value.name', '')
        df.columns = df.columns.str.replace('.value', '')
        df.columns = df.columns.str.replace('.', '_')

        del df['type']

        df = df.reset_index(drop=True)
        return df

    def get_absence_entitlements(self, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """
        The same endpoint as get, but now with the absence_entitlement attribute included. This attribute can have multiple lines per employee.
        This function ONLY returns the absence_entitlement per employee per absence type.
        :param limit: The maximum number of employees to fetch. Default is 100.
        :param offset: The offset to start fetching the employees. Default is 0.
        :return: A pandas DataFrame containing the fetched employees.
        """
        url = f'{self.base_url}company/employees?attributes[]=absence_entitlement&limit={limit}&offset={offset}'
        data = []
        while True:
            response = requests.get(url, headers=self.headers, timeout=3600)
            response.raise_for_status()
            for employee in response.json()['data']:
                employee_id = employee['attributes']['id']['value']
                for entitlement in employee['attributes']['absence_entitlement']['value']:
                    entitlement_data = {
                        "employee_id": employee_id,
                        "absence_type": entitlement['attributes']['name'],
                        "absence_category": entitlement['attributes']['category'],
                        "entitlement": entitlement['attributes']['entitlement']
                    }
                    data.append(entitlement_data)
            total_pages = response.json()['metadata']['total_pages']
            if offset < total_pages:
                offset += limit
                url = f'{self.base_url}company/employees?attributes[]=absence_entitlement&limit={limit}&offset={offset}'
            else:
                break

        # drop each column which ends with .label, .type and .universal_id
        df = pd.DataFrame(data)
        return df

    def get_holiday_calendar(self, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """
        The same endpoint as get, but now with the holiday_calendar attribute. This attribute can have multiple lines per employee.
        This function ONLY returns the holiday_calendar per employee.
        :param limit: The maximum number of employees to fetch. Default is 100.
        :param offset: The offset to start fetching the employees. Default is 0.
        :return: A pandas DataFrame containing the fetched employees.
        """
        url = f'{self.base_url}company/employees?attributes[]=holiday_calendar&limit={limit}&offset={offset}'
        data = []
        while True:
            response = requests.get(url, headers=self.headers, timeout=3600)
            for employee in response.json()['data']:
                employee_id = employee['attributes']['id']['value']
                calendar = employee['attributes']['holiday_calendar']['value']['attributes']
                calendar_data = {
                    "employee_id": employee_id,
                    "calendar_id": calendar['id'],
                    "calendar_name": calendar['name'],
                    "country": calendar['country'],
                    "state": calendar['state']
                }
                data.append(calendar_data)
            total_pages = response.json()['metadata']['total_pages']
            if offset < total_pages:
                offset += limit
                url = f'{self.base_url}company/employees?attributes[]=holiday_calendar&limit={limit}&offset={offset}'
            else:
                break

        df = pd.DataFrame(data)
        return df

    def create(self, data):
        """
        Will be implemented later.
        """
        url = f'{self.base_url}company/employees'
        response = requests.post(url, json=data, headers=self.headers, timeout=3600)
        response.raise_for_status()
        return response.json()

    def update(self, employee_id, data):
        """
        Will be implemented later.
        """
        url = f'{self.base_url}company/employees/{employee_id}'
        response = requests.patch(url, json=data, headers=self.headers, timeout=3600)
        response.raise_for_status()
        return response.json()

    def get_absence_balance(self, employee_id):
        """
        Will be implemented later.
        """
        url = f'{self.base_url}company/employees/{employee_id}/absence_balances'
        response = requests.get(url, headers=self.headers, timeout=3600)
        response.raise_for_status()
        return response.json()

    def get_attributes(self):
        """
        Will be implemented later.
        """
        url = f'{self.base_url}company/employee_attributes'
        response = requests.get(url, headers=self.headers, timeout=3600)
        response.raise_for_status()
        return response.json()

    def get_custom_attributes(self):
        """
        Will be implemented later.
        """
        url = f'{self.base_url}company/employee_custom_attributes'
        response = requests.get(url, headers=self.headers, timeout=3600)
        response.raise_for_status()
        return response.json()
