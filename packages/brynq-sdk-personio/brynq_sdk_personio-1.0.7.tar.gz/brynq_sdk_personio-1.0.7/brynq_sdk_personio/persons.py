from typing import List
import requests
import pandas as pd
import json


class Persons:

    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url

    def get(self, limit: int = 50, updated_at: str = None, ids: List[str] = None) -> pd.DataFrame:
        """
        This endpoint returns a list of persons.
        :param limit: The maximum number of compensations to fetch. Default is 100.
        :param ids: Filter results matching one or more provided person ids.
        :param updated_at: An updatead date for which to get persons.
        """
        base_url = f'{self.base_url}persons'
        payload = {
            'limit': limit
        }
        if updated_at:
            payload['updated_at'] = updated_at
        if ids:
            payload['id'] = ','.join(ids)
        df = pd.DataFrame()
        url = base_url
        while True:
            response = requests.get(url, headers=self.headers, data=json.dumps(payload), timeout=3600)
            response.raise_for_status()
            df_temp = pd.json_normalize(response.json().get('_data'))
            df = pd.concat([df, df_temp])
            cursor = response.json().get('_meta', {}).get('links', {}).get('next', {}).get('href')
            if cursor:
                url = cursor
            else:
                break

        df.columns = df.columns.str.replace('.', '_')
        df = df.reset_index(drop=True)

        return df