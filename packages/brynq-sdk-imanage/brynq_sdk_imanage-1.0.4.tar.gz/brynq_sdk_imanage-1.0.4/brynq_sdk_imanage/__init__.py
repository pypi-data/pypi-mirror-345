import requests
import json
from typing import List, Union
from brynq_sdk_brynq import BrynQ


from typing import List, Union
import requests

class IManage(BrynQ):
    def __init__(self, interface_id:str,system_type:str='source', debug: bool = False):
        super().__init__()
        self.debug = debug
        self.credentials = self.interfaces.credentials.get(interface_id=interface_id, system='i-manage-oauth', system_type=system_type)
        self.customer_name = self.subdomain.lower()
        self.imanage_url = f'https://cloudimanage.com'
        self.customer_id, self.customer_url = self._get_customer_id_and_url()
        self.timeout = 3600


    def __get_headers(self):
        return {
            'X-Auth-Token': f'{self.credentials["data"]["access_token"]}'
        }

    def _get_customer_id_and_url(self):
        headers = self.__get_headers()
        url = f'{self.imanage_url}/api'
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        if self.debug:
            print(response.text)
        data = response.json()

        # Extract customer_id as before
        customer_id = data['data']['user']['customer_id']
        customer_id = str(customer_id)

        v2_versions = []

        # Loop through the versions to find 'v2' versions
        versions = data['data']['versions']
        for version in versions:
            if version['name'] == 'v2':
                version_number = version['version']  # This should be a string like '2.1.1160'
                version_url = version['url']
                v2_versions.append((version_number, version_url))

        # Sort the v2 versions by their version number in descending order to get the newest version first
        v2_versions.sort(key=lambda x: [int(part) for part in x[0].split('.')], reverse=True)

        # If there are any v2 versions, select the newest one
        if v2_versions:
            customer_url = v2_versions[0][1]  # The URL of the newest v2 version
        else:
            # Raise an exception if no v2 version is found
            raise Exception("No 'v2' version found for the customer.")

        return customer_id, customer_url

    def get_all_users(self):
        headers = self.__get_headers()
        limit = 100
        offset = 0
        users = []
        payload = {}
        while True:
            url = f'{self.customer_url}/customers/{self.customer_id}/users?require_role=true&limit={limit}&offset={offset}&total=true'
            response = requests.get(url, headers=headers, data = payload, timeout=self.timeout)
            response.raise_for_status()
            if self.debug:
                print(response.text)
            data = response.json()
            users.extend(data['data'])
            if offset >= data['total_count']:
                break
            offset += limit
        return users


