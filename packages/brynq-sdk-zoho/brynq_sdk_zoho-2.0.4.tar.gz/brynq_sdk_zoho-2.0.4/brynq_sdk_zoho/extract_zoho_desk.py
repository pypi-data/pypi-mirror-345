import os
import sys
import pandas as pd
from typing import Union, List
import requests
import json
from brynq_sdk_brynq import BrynQ

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class ExtractZohoDesk(BrynQ):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.headers = self._get_authentication(label=label)
        self.base_url = "https://desk.zoho.com/api/v1/"
        self.payload = {}
        self.timeout = 3600

    def _get_authentication(self, label):
        """
        Get the credentials for the Tracket API from BrynQ, with those credentials, get the access_token for Tracket.
        Return the headers with the access_token.
        """
        # Get credentials from BrynQ
        credentials = self.get_system_credential(system='zoho-desk', label=label)

        # With those credentials, get the access_token from Tracket
        zoho_system_id = credentials["id"]
        token = BrynQ().refresh_system_credential(system="zoho-desk", system_id=zoho_system_id)["access_token"]
        headers = {
            'Authorization': f'Zoho-oauthtoken {token}'
        }
        return headers

    def get_zoho_accounts(self, query_params=""):
        """
        This function gets all the accounts from zoho and saves them as df_zoho_accounts
        :return: df_zoho_accounts
        """
        base_url = f"{self.base_url}accounts"
        return self._multiple_calls(base_url, query_params)

    def get_zoho_agents(self, query_params=""):
        """
        This function gets the user data from zoho and saves the data to df_zoho_users
        :return:
        """
        base_url = f"{self.base_url}agents"
        return self._multiple_calls(base_url, query_params)

    def get_zoho_agent(self, agent_id, query_params=""):
        """
        This function gets the user data from zoho and saves the data to df_zoho_users
        :return:
        """
        url = f"{self.base_url}agents/{agent_id}?{query_params}"
        return self._single_call(url)

    def get_zoho_contacts(self, query_params=""):
        """
        This function gets the zoho contact information from zoho desk and saves the data to df_zoho_contacts
        :return:
        """
        base_url = f"{self.base_url}contacts"
        return self._multiple_calls(base_url, query_params)

    def get_recent_zoho_tickets(self, query_params=""):
        """
        This function gets the newest 100 tickets form Zoho-Desk
        :return:
        """
        url = f"{self.base_url}tickets?limit=100&from=0&{query_params}"
        return self._single_call(url)

    def get_all_zoho_tickets(self, query_params: str = "") -> pd.DataFrame:
        """
        This function gets the zoho contact information from zoho desk and saves the data to df_zoho_contacts
        :return:
        """
        base_url = f"{self.base_url}tickets"
        return self._multiple_calls(base_url, query_params)

    def get_archived_zoho_tickets(self, query_params: str = "") -> pd.DataFrame:
        """
        This function gets the zoho contact information from zoho desk and saves the data to df_zoho_contacts
        :return:
        """
        base_url = f"{self.base_url}tickets/archivedTickets"
        return self._multiple_calls(base_url, query_params)

    def get_active_ticket_timers(self, tickets: pd.DataFrame, query_params: str = "") -> pd.DataFrame:
        """=
        This function gets all the active ticket timers from the tickets given in the tickets dataframe.
        :param tickets: dataframe with the ticket_id's
        :param query_params: query parameters for the API call
        :return: pd.DataFrame with the ticket timers
        """
        df = pd.DataFrame()
        count = 0
        for index, ticket in tickets.iterrows():
            count = count + 1
            print(f"Checking for ticket number {ticket.ticket_id}. ticket {count} / " + str(
                len(tickets.index)))
            url = f"{self.base_url}tickets/{ticket.ticket_id}/activeTimer?{query_params}"
            df_temp = self._single_call(url)
            df_temp['ticket_id'] = ticket.ticket_id
            df_temp['link'] = ticket.link
            df_temp['ticket_number'] = ticket.ticket_number
            df = pd.concat([df, df_temp])
        df = df.reset_index(drop=True)
        return df

    def get_zoho_ticket_timers(self, tickets, query_params=""):
        """
        This function gets all the ticket timers from the recent tickets if there already exists a database. Otherwise,
        it will get all the ticket timers. the ticket timers are saved to df_zoho_ticket_timers
        :return:
        """
        df = pd.DataFrame()
        count = 0
        for ticket_id in tickets["ticket_id"]:
            count = count + 1
            print(f"Checking for ticket number {ticket_id}. ticket {count} / " + str(
                len(tickets.index)))
            url = f"{self.base_url}tickets/{ticket_id}/timeEntry?{query_params}"
            df_temp = self._single_call(url)
            df = pd.concat([df, df_temp])
        df = df.reset_index(drop=True)
        return df

    def _multiple_calls(self, base_url, query_params) -> pd.DataFrame:
        """
        This function helps the API calls to do multiple calls in one function
        :return:
        """
        df = pd.DataFrame()
        end_of_loop = False
        offset = 0
        while not end_of_loop:
            url = f"{base_url}?from={offset}&limit=90&{query_params}"
            df_temp = self._single_call(url)
            df = pd.concat([df_temp, df])
            if len(df_temp) != 90:
                end_of_loop = True
            else:
                offset += 90
        return df

    def _single_call(self, url: str) -> pd.DataFrame:
        """
        This function helps the API calls to do a single call in one function
        :return:
        """
        response = requests.request("GET", url, headers=self.headers, data=self.payload, timeout=self.timeout)
        if response.status_code == 401:
            response = requests.request("GET", url, headers=self.headers, data=self.payload, timeout=self.timeout)
        if response.status_code == 200:
            df = response.json()
            if 'data' in df:
                df = pd.json_normalize(df['data'])
            else:
                df = pd.json_normalize(df)
            return df
        elif response.status_code == 204:
            return pd.DataFrame()
        else:
            raise Exception(response.text)
