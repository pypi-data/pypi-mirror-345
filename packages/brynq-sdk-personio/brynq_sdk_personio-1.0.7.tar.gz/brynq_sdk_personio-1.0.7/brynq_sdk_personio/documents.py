import requests
import pandas as pd
import json
from typing import BinaryIO, Optional
import warnings


class Documents:

    def __init__(self, headers, base_url):
        self.headers = headers
        self.base_url = base_url

    def get_categories(self) -> pd.DataFrame:
        """
        This endpoint is responsible for fetching all document categories of the company. The result contains a list of document categories.
        """
        url = f'{self.base_url}company/document-categories'
        response = requests.get(url, headers=self.headers, timeout=3600)
        response.raise_for_status()
        df = pd.json_normalize(response.json()['data'])
        df = df.rename(columns={
            'attributes.name': 'description'
        })
        del df['type']
        return df

    def list(self, employee_id: str, category_id: str = None, created_at_gt: str = None, created_at_lt: str = None, limit: int = 100) -> pd.DataFrame:
        """
        Lists the metadata of Documents belonging to the provided owner ID.
        """
        # this endpoint is v2
        base_url = self.base_url.replace("v1", "v2")
        url = f'{base_url}document-management/documents'
        params = {'owner_id': employee_id, 'limit': limit}
        if category_id:
            params['category_id'] = category_id
        if created_at_gt:
            params['created_at.gt'] = created_at_gt
        if created_at_lt:
            params['created_at.lt'] = created_at_lt

        df = pd.DataFrame()
        while True:
            response = requests.get(url, headers=self.headers, params=params, timeout=3600)
            response.raise_for_status()
            df_temp = pd.json_normalize(response.json()['_data'])
            df = pd.concat([df, df_temp])
            cursor = response.json().get('_meta', {}).get('links', {}).get('next', {}).get('href')
            if cursor:
                url = cursor
            else:
                break

        df.columns = df.columns.astype(str).str.replace('.', '_')

        return df

    def upload(self, title: str, employee_id: str, category_id: str, file: BinaryIO, comment: Optional[str] = None, date: Optional[str] = None) -> requests.Response:
        """
        This endpoint is responsible for uploading documents for the company employees.
        :param title: Title of the document. Maximum length is 255 characters.
        :param employee_id: Employee identifier
        :param category_id: Document Category identifier
        :param file: The document that shall be uploaded to an employees profile. Maximum file size is 30MB.
        :param comment: Optional comment that can be added to the uploaded document.
        :param date: Optional date can be added to the uploaded document. Must follow the format: Y-m-d
        """
        if len(title) > 255:
            warnings.warn('title must be a maximum of 255 characters')
            title = title[:254]

        # check if file is a file object and smaller than 30MB
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        if file_size > 30 * 1024 * 1024:
            raise ValueError('file must be smaller than 30MB')

        url = f'{self.base_url}company/documents'
        payload = {
            "title": title,
            "employee_id": employee_id,
            "category_id": category_id
        }
        if comment:
            payload['comment'] = comment
        if date:
            payload['date'] = date

        headers = self.headers
        headers.pop('Content-Type')
        headers.update({'accept': 'application/json'})

        response = requests.post(url, headers=headers, data=payload, files={"file": (title, file, "application/pdf")}, timeout=3600)

        return response
