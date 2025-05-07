from brynq_sdk_brynq import BrynQ
from typing import Union, List
import requests
import json


class Maxxton(BrynQ):
    """
    BrynQ wrapper for Maxxton
    """
    def __init__(self, label: Union[str, List] = None, test_environment: bool = False, debug=False):
        super().__init__()

        if test_environment:
            self.base_url = 'https://api-test.maxxton.net/'
        else:
            self.base_url = 'https://api.maxxton.net/'

        credentials = self.get_system_credential(system='maxxton', label=label)
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.scope = credentials['scope']
        self.timeout = 3600

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._get_maxxton_access_token()}'
        }

    def create_new_employee(self, data: dict) -> requests.Response:
        """
        Create a new employee in Maxxton
        https://developers.maxxton.com/maxxton/v1/swagger/index.html#/Employee/createEmployees
        :param data: The data of the employee
        :return: The response of the request
        """
        url = f'{self.base_url}maxxton/v1/employees'
        return requests.post(url=url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)

    def update_employee(self, employee_id: str, data: dict) -> requests.Response:
        """
        Update an existing employee in Maxxton
        https://developers.maxxton.com/maxxton/v1/swagger/index.html#/Employee/updateEmployees
        :param employee_id: The id of the employee
        :param data: The data of the employee
        :return: The response of the request
        """
        url = f'{self.base_url}maxxton/v1/employees/{employee_id}'
        return requests.put(url=url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)

    def _get_maxxton_access_token(self) -> str:
        """
        Get the access token for Maxxton
        https://developers.maxxton.com/maxxton/v1/swagger/index.html#/Authentication/authenticate
        :return: The access token
        """
        url = f'{self.base_url}maxxton/v1/authenticate'

        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope
        }
        response = requests.request("POST", url=url, params=params, timeout=self.timeout)

        return response.json()['access_token']
