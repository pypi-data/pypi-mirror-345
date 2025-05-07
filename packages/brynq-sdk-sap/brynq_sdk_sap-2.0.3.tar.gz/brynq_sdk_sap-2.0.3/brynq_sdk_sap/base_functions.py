from brynq_sdk_brynq import BrynQ
import os
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from lxml import etree
import pandas_read_xml as pdx
import pandas as pd
import datetime
import requests
from requests.exceptions import HTTPError
import json


class BaseFunctions(BrynQ):
    def __init__(self, label: str, data_dir: str, certificate_file: str = None, key_file: str = None, client_secret: str = None, debug: bool = False):
        """
        The SAP class is used to get the access token for the SAP connection.
        :param label: The label of the SAP connection in BrynQ
        :param data_dir: The directory where the data will be stored. Needed for pandas to read the XML file
        :param certificate_file: The certificate file: open(file, 'rb')
        :param key_file: The key file in bytes format: open(file, 'rb')
        """
        super().__init__()
        self.timeout = 3600
        self.debug = debug
        credentials = self.get_system_credential(system='sap', label=label)
        self.label = label
        self.credentials = credentials
        self.certificate_file = certificate_file
        self.key_file = key_file
        self.client_secret = client_secret
        self.base_url = credentials['base_url']
        self.headers = self.get_authorization_headers(credentials['client_id'], credentials['authorisation_url'], certificate_file, key_file, credentials['client_secret'])
        self.data_dir = data_dir

    def get_authorization_headers(self, client_id, authorisation_url, certificate_file=None, key_file=None, client_secret=None):
        """
        Get the access token from the endpoint
        1) Visit brynq to get the base_url, autorisation_url and client_id
        2) Get the access token from the endpoint using the client_id and certificate files
        :return: returns the retrieved access_token
        """
        if client_secret is not None:
            # Get the access token with help of the client_secret
            payload = f'grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            token = requests.post(authorisation_url, headers=headers, data=payload, timeout=self.timeout).json()
        else:
            client = BackendApplicationClient(client_id=client_id)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(token_url=authorisation_url,
                                      include_client_id=True,
                                      cert=(certificate_file, key_file))
        headers = {
            'Authorization': f'Bearer {token["access_token"]}',
            'Content-Type': 'application/json'
        }
        return headers

    def renew_authorization_headers(self):
        """
        Renew the access token
        :return: returns the retrieved access_token
        """
        credentials = self.get_system_credential(system='sap', label=self.label)
        self.headers = self.get_authorization_headers(credentials['client_id'], credentials['authorisation_url'], self.certificate_file, self.key_file, credentials['client_secret'])

    def get_data(self, uri: str, filter: str = None, xml_root: list = []):
        """
        :param uri: The endpoint to call
        :param xml_root: the response from SAP comes within XML format. Give the root of the XML file from which you want to get the data
        :param filter: filter for the endpoint
        :return: a pandas dataframe with the content from the called endpoint
        i.e. fetch_data('OrgStructureSet', xml_root='OrgStructures', filter="Startdate eq '2022-01-01'")
        """
        url = f"{self.base_url}/{uri}?$filter={filter}" if filter is not None else f"{self.base_url}/{uri}"
        response = requests.request("GET", f"{url}", headers=self.headers, data={}, timeout=self.timeout)
        if response.status_code == 401:
            self.renew_authorization_headers()
            response = requests.request("GET", f"{url}", headers=self.headers, data={}, timeout=self.timeout)
        if self.debug:
            print(response.text)
        if response.status_code >= 300:
            if len(response.text) > 0:
                doc = etree.XML(response.content)
                error_code = doc.getchildren()[0].text
                error_message = doc.getchildren()[1].text
                raise HTTPError(f'Error from SAP while calling endpoint {uri}. The message is \"{error_message}\" with code {error_code}', response=response)
            else:
                raise HTTPError(f'Error from SAP while calling endpoint {uri}. There is no message with code {response.status_code}', response=response)
        if response.text == '':
            df = pd.DataFrame()
        else:
            with open(f"{self.data_dir}/{uri}.xml", 'wb') as file:
                file.write(response.content)
            # The response from SAP can contain multiple XML elements but also one element. That will cause errors in parsing. If there is one element, go to the except
            try:
                df = pdx.read_xml(f"{self.data_dir}/{uri}.xml", xml_root, root_is_rows=False)
                df = df.pipe(pdx.fully_flatten).reset_index(drop=True)
            except ValueError:
                xml_root = xml_root[:-1]
                df = pdx.read_xml(f"{self.data_dir}/{uri}.xml", xml_root, root_is_rows=False, transpose=True)
                df.reset_index(inplace=True, drop=True)

        return df

    def post_data(self, uri: str, data: dict, filter: str = None, return_key: str = None):
        """
        Post data to the endpoint in SAP. For many endpoint, SAP returns an ID for the created object. This function will add the ID to the response so you can re-use it.
        :param uri: The endpoint to call
        :param data: The body of the request filled with the data you want to post
        :param filter: The filter you want to use to filter the data on
        :param return_key: The key of the ID you expect SAP to return after the POST. i.e. 'employee_id'
        :return: An ID if return_key is given, otherwise the response from SAP
        """
        url = f"{self.base_url}/{uri}?$filter={filter}" if filter is not None else f"{self.base_url}/{uri}"
        response = requests.request("POST", url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        if self.debug:
            return response
        if response.status_code == 401:
            self.renew_authorization_headers()
            response = requests.request("POST", url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        # Don't use raise_for_status() here because the errors from SAP will come in XML format which can be parsed here
        if response.status_code == 201:
            if len(response.text) == 0 or return_key is None:
                return response
            elif response.text.startswith('{'):
                response = json.loads(response.text)
                return_id = response[return_key]
                return return_id
            else:
                doc = etree.XML(response.content)
                return_id = doc.getchildren()[0].find(return_key).text
                return return_id
        else:
            # The error message is in XML format, follows the below steps to extract the error message
            if len(response.text) > 0:
                try:
                    doc = etree.XML(response.content)
                    error_code = doc.getchildren()[0].text
                    error_message = doc.getchildren()[1].text
                    error_details = doc.getchildren()[2].getchildren()[4].getchildren()[0].getchildren()[1].text
                    error_details_status = doc.getchildren()[2].getchildren()[4].getchildren()[0].getchildren()[3].text
                    error_details_status = "" if error_details_status is None else f"\r\nReal Status: {error_details_status}\r\n"
                except Exception:
                    error_code = ""
                    error_message = "Error in the response from SAP parsing the XML"
                    error_details = ""
                    error_details_status = ""
                raise HTTPError(
                    f'Error from SAP while calling endpoint {uri}. \r\nThe message is \"{error_message}\" with code {error_code}, \r\nDetails: {error_details}{error_details_status}', response=response)
            else:
                raise HTTPError(f'Error from SAP while calling endpoint {uri}. There is no message with code {response.status_code}', response=response)

    def delete_data(self, uri: str, filter: str):
        """
        Delete data from the endpoint based on a filter. Be aware that for some endpoints you really delete the data but for others
        you will only delimit the selected dataset with an enddate but the data will still exist
        :param uri: The endpoint to call
        :param filter: The filter to delete the data on
        :return: the response from the call
        """
        url = f"{self.base_url}/{uri}/{filter}" if filter is not None else f"{self.base_url}/{uri}"
        response = requests.request("DELETE", f"{url}", headers=self.headers, timeout=self.timeout)
        if response.status_code == 401:
            self.renew_authorization_headers()
            response = requests.request("DELETE", f"{url}", headers=self.headers, timeout=self.timeout)
        return response

    def exclude_expired_objects(self, df, col='end_date', expiration_date=datetime.datetime.today()):
        """
        Allready delimited objects are not relevant for editing but often they will be returned within the data from the API.
        This function will exclude all the objects that are already delimited from the dataframe you will enter.
        :param df: the dataframe you want to remove the expired objects from
        :param col: the column which determines if the object is expired. most of the time this is the end_date
        :param expiration_date: The date which counts as threshold for if an object is expired or not. Most of the time it is today
        :return: the dataframe without the expired objects
        """
        # 1. Get the objects with high date 9999-12-31, these are valid
        df[col] = df[col].replace('0000-00-00', '9999-12-31')
        df_high_date = df[df[col].str.startswith('9999')]
        # 2. Get the objects with col not 9999-12-31, and transform them into date, select the ones which is higher than expiration_date
        df_tmp = df[~df[col].str.startswith('9999')]
        if len(df_tmp) > 0:
            df_tmp[col] = pd.to_datetime(df_tmp[col])
            df_tmp = df_tmp[df_tmp[col] > expiration_date]
        # 3. Concat the two dataframes and return them
        df = pd.concat([df_high_date, df_tmp])
        return df
