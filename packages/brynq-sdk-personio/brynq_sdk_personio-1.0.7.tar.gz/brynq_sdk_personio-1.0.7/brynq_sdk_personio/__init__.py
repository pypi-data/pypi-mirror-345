import requests
import json
from typing import List, Union
from brynq_sdk_brynq import BrynQ
from .employees import Employees
from .compensations import Compensations
from .custom_reports import CustomReports
from .documents import Documents


# Set the base class for Persinio. This class will be used to set the credentials and those will be used in all other classes.
class Personio(BrynQ):
    def __init__(self, label: Union[str, List], debug: bool = False):
        """"
        For the documentation of Personio, see: https://developer.personio.de/reference/auth
        """
        super().__init__()
        base_url = 'https://api.personio.de/'
        access_token_v1 = self._get_credentials(label, base_url, version='v1')
        access_token_v2 = self._get_credentials(label, base_url, version='v2')
        headers_v1, headers_v2 = self._set_headers(access_token_v1, access_token_v2)
        self.employees = Employees(headers_v1, f'{base_url}v1/')
        self.custom_reports = CustomReports(headers_v1, f'{base_url}v1/')
        self.documents = Documents(headers_v1, f'{base_url}v1/')
        self.compensations = Compensations(headers_v2, f'{base_url}v2/')


    def _get_credentials(self, label, base_url, version='v2'):
        """
        Sets the credentials for the Personio API.
        :param label (str): The label for the system credentials.
        :returns: headers (dict): The headers for the API request, including the access token.
        """
        credentials = self.get_system_credential(system='personio', label=label)
        payload = {
            "client_id": f"{credentials['client_id']}",
            "client_secret": f"{credentials['client_secret']}",
            "grant_type": "client_credentials"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded"
        }
        url = f'{base_url}{version}/auth/token'
        if version == 'v1':
            url = f'{base_url}{version}/auth'
            headers["content-type"] = "application/json"
            payload = json.dumps(payload)
        response = requests.post(url, headers=headers, data=payload, timeout=3600)
        response.raise_for_status()
        access_token = response.json()['data']['token'] if version == 'v1' else response.json()['access_token']

        return access_token

    def _set_headers(self, access_token_v1, access_token_v2):
        headers_v1 = {
            'Authorization': f'Bearer {access_token_v1}',
            'Content-Type': 'application/json',
            'X-Personio-Partner-ID': 'BRYNQ',
            'X-Personio-App-ID': 'BRYNQ_COM'
        }
        headers_v2 = {
            'Authorization': f'Bearer {access_token_v2}',
            'accept': 'application/json',
            'X-Personio-Partner-ID': 'BRYNQ',
            'X-Personio-App-ID': 'BRYNQ_COM'
        }
        return headers_v1, headers_v2