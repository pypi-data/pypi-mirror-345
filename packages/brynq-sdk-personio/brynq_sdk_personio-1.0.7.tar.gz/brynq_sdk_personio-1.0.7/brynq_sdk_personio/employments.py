from typing import List
import requests
import pandas as pd
import json


class Employments:

    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url

    def get(self, person_id: str, limit: int = 50, updated_at: str = None, ids: List[str] = None) -> pd.DataFrame:
        """
        Returns a list of employments of a given person. The employments are returned in sorted order, with the most recent employments appearing first.
        :param limit: The maximum number of compensations to fetch. Default is 100.
        :param updated_at: Filter employments by updated date. Format is ISO-8601.
        :param person_id: Filter results matching a person id
        :param ids: Filter results matching one or more provided employment ids.
        """
        base_url = f'{self.base_url}persons/{person_id}/employments'
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
            df_temp = pd.json_normalize(response.json()['_data'])
            df = pd.concat([df, df_temp])
            cursor = response.json().get('_meta', {}).get('links', {}).get('next', {}).get('href')
            if cursor:
                url = cursor
            else:
                break

        df.columns = df.columns.str.replace('.', '_')
        df = df.reset_index(drop=True)

        return df