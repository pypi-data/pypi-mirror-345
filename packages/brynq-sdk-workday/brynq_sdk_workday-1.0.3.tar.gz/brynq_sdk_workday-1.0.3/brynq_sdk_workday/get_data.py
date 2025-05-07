import requests
import pandas as pd
from typing import List, Union
from brynq_sdk_brynq import BrynQ


class GetData(BrynQ):
    def __init__(self, label: Union[str, List], debug: bool = False):
        super().__init__()
        self.timeout = 3600
        self.base_url, self.headers = self._set_credentials(label)


    def _set_credentials(self, label):
        """
        Sets the credentials for the Workday API.

        Parameters:
        label (str): The label for the system credentials.

        Returns:
        base_url (str): The base URL for the API.
        headers (dict): The headers for the API request, including the access token.
        """
        credentials = self.get_system_credential(system='workday', label=label)

        credential_id = credentials['id']
        host = credentials['host']
        username = credentials['username']
        password = credentials['password']
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']
        token_url = credentials['token_url']
        report_url = credentials['report_url']

        # Get the Access Token
        token_url = f'{host}/{token_url}'
        report_url = f'{host}/{report_url}'
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", token_url, headers=headers, data=payload, timeout=self.timeout)
        access_token = response.json()['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        return report_url, headers

    def get_data(self, endpoint: str, top_level_key: str, format: str = 'json', select: str = None, filter: str = None):
        """
        Download data from successfactors via the report method.
        :param endpoint: give the endpoint you want to call
        :param top_level_key: the top level key in the response json
        :param format: optional. Choose between json and xml
        :param select: optional. Give a list of fields you want to select. Comma seperated, no spaces in between. Example: seqNumber,startDate,userId
        :param filter: Optional. Enter a filter in OData format. See here more information:
        """
        url = f'{self.base_url}/{endpoint}?format={format}&'
        if select:
            url = f'{url}$select={select}&'
        if filter:
            url = f'{url}$filter={filter}&'

        df = pd.DataFrame()
        while True:
            response = requests.request("GET", url, headers=self.headers, timeout=self.timeout)
            data = response.json()[top_level_key]
            df_temp = pd.DataFrame(data)
            df = pd.concat([df, df_temp])
            url = response.json().get('__next', None)
            if not url:
                break

        return df
