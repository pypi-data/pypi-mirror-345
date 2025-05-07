import requests
import pandas as pd
import re
from typing import List, Union
from brynq_sdk_brynq import BrynQ


class GetData(BrynQ):
    def __init__(self, label: Union[str, List], debug: bool = False):
        """"
        For the documentation of SAP, see: https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM/d599f15995d348a1b45ba5603e2aba9b/0491f8c9f81b4112a18cabcefc082490.html
        """
        super().__init__()
        self.timeout = 3600
        self.base_url, self.headers = self._set_credentials(label)

    def _set_credentials(self, label):
        """
        Sets the credentials for the SuccessFactors API.

        Parameters:
        label (str): The label for the system credentials.

        Returns:
        base_url (str): The base URL for the API.
        headers (dict): The headers for the API request, including the access token.
        """
        credentials = self.get_system_credential(system='successfactors', label=label)
        base_url = credentials['base_url']
        token_url = credentials['auth_url']
        client_id = credentials['client_id']
        company_id = credentials['company_id']
        user_id = credentials['username']
        private_key = credentials['password']

        # Get the SAML assertion
        url = f'{base_url}/oauth/idp'
        payload = {
            'client_id': client_id,
            'user_id': user_id,
            'token_url': token_url,
            'private_key': private_key
        }
        response = requests.request("POST", url, data=payload, timeout=self.timeout)
        saml_assertion = response.text

        # Now get the access_token
        payload = {
            'client_id': client_id,
            'grant_type': 'urn:ietf:params:oauth:grant-type:saml2-bearer',
            'company_id': company_id,
            'assertion': saml_assertion
        }
        response = requests.request("POST", url=token_url, data=payload, timeout=self.timeout)
        access_token = response.json()['access_token']
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        return base_url, headers

    @staticmethod
    def _convert_date_columns(df):
        max_timestamp = pd.Timestamp.max.value // 10**6
        for col in df.columns:
            if df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, str)).any():  # if the column is of object type
                # Check if any cell in the column matches the pattern
                if df[col].str.contains(r'/Date\(\d+(\+\d+)?\)/', regex=True).any():
                    # Extract the timestamp and convert it to datetime
                    df[col] = df[col].str.extract(r'(\d+)', expand=False).astype('float')
                    # If timestamp is too large, set value to None
                    df[col] = df[col].apply(lambda x: pd.to_datetime(x, unit='ms') if x <= max_timestamp else None)
        return df

    def get_odata(self, endpoint: str, select: str = None, filter: str = None):
        """
        Download data from successfactors via the OData method.
        :param endpoint: give the endpoint you want to call
        :param select: optional. Give a list of fields you want to select. Comma seperated, no spaces in between. Example: seqNumber,startDate,userId
        :param filter: Optional. Enter a filter in OData format. See here more information: https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM/d599f15995d348a1b45ba5603e2aba9b/ded5808b5edb4bc9a8acfb5e9fe1b025.html
        """
        url = f'{self.base_url}/odata/v2/{endpoint}?'
        if select:
            url = f'{url}$select={select}&'
        if filter:
            url = f'{url}$filter={filter}&'

        df = pd.DataFrame()
        while True:
            response = requests.request("GET", url, headers=self.headers, timeout=self.timeout)
            data = response.json()['d']['results']
            df_temp = pd.DataFrame(data)
            df = pd.concat([df, df_temp])
            url = response.json()['d'].get('__next', None)
            if not url:
                break

        # Reformat eventual date columns to pd.datetime
        df = self._convert_date_columns(df)
        return df
