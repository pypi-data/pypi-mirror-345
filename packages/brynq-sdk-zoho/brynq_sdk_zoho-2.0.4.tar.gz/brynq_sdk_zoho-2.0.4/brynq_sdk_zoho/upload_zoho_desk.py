import os
import sys
import pandas as pd
from typing import Union, List
import requests
import json
from brynq_sdk_brynq import BrynQ

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class UploadZohoDesk(BrynQ):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.headers = self._get_authentication(label=label)
        self.base_url = "https://desk.zoho.com/api/v1/"
        self.timeout = 3600

    def _get_authentication(self, label):
        """
        Get the credentials for the Traket API from BrynQ, with those credentials, get the access_token for Tracket.
        Return the headers with the access_token.
        """
        # Get credentials from BrynQ
        credentials = self.get_system_credential(system='zoho-desk', label=label)

        # With those credentials, get the access_token from Tracket
        zoho_system_id = credentials["id"]
        token = BrynQ().refresh_system_credential(system="zoho-desk", system_id=zoho_system_id)["access_token"]
        headers = {
            'Authorization': f'Zoho-oauthtoken {token}',
            'Content-Type': 'application/json'
        }
        return headers

    def update_ticket_time_entry(self, ticket_id, time_entry_id, payload):
        """
        This function updates the time entry of a ticket in zoho desk
        :param ticket_id: str
        :param time_entry_id: str
        :param payload: dict
        """
        url = f"{self.base_url}tickets/{ticket_id}/timeEntry/{time_entry_id}"
        response = requests.request("PATCH", url, headers=self.headers, data=json.dumps(payload), timeout=self.timeout)
        return response
