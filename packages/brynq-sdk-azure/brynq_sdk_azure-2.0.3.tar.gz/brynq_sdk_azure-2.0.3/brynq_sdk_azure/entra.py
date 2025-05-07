from brynq_sdk_brynq import BrynQ
import urllib.parse
import warnings
import requests
import random
import string
import json
import pandas as pd
from pandas import json_normalize
from msal import ConfidentialClientApplication
from typing import Union, List
import os

class Entra(BrynQ):

    def __init__(self, label: Union[str, List], debug: bool = False):
        super().__init__()
        self.headers = self.__get_headers(label=label)
        self.endpoint = "https://graph.microsoft.com/v1.0"
        self.timeout = 3600

    def __get_headers(self, label):
        credentials = self.get_system_credential(system='azure-entra-token', label=label)
        tenant_id = credentials['tenant_id']
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        authority = f"https://login.microsoftonline.com/{tenant_id}"

        # Create a ConfidentialClientApplication for authentication
        app = ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )

        # Get an access token for the Graph API
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        headers = {
            'Authorization': f"Bearer {result['access_token']}",
            'Content-Type': 'application/json'
        }

        return headers

    def __add_attribute_information(self, payload, custom_attributes):
        # First get the official name of the custom attribute and all the other information
        payload.update({"customSecurityAttributes": {}})
        metadata = requests.get('https://graph.microsoft.com/v1.0/directory/customSecurityAttributeDefinitions', headers=self.headers, timeout=self.timeout).json()
        # Now loop through the given metadata and add the corresponding metadata and the values itself to the payload
        for attr, value in custom_attributes.items():
            for meta in metadata["value"]:
                if meta["name"] == attr:
                    attr_set = meta["attributeSet"]
                    attr_type = meta["type"]
                    is_collection = meta["isCollection"]
                    if attr_set not in payload["customSecurityAttributes"]:
                        payload["customSecurityAttributes"][attr_set] = {"@odata.type": "#microsoft.graph.customSecurityAttributeValue"}
                    # In case of an integer, the field type should be given as well
                    if attr_type == "Integer":
                        if is_collection:
                            payload["customSecurityAttributes"][attr_set][f"{attr}@odata.type"] = "#Collection(Int32)"
                        else:
                            payload["customSecurityAttributes"][attr_set][f"{attr}@odata.type"] = "#Int32"
                        payload["customSecurityAttributes"][attr_set][attr] = value
                    # In case of a boolean, only the value should be given, the field type itself is not relevant
                    elif attr_type == "Boolean":
                        payload["customSecurityAttributes"][attr_set][attr] = value
                    # In case of a string, the field type should be given if the field is a collection of values. If it's a single value, the field type is not relevant
                    else:
                        if is_collection:
                            payload["customSecurityAttributes"][attr_set][f"{attr}@odata.type"] = "#Collection(String)"
                        payload["customSecurityAttributes"][attr_set][attr] = value
        return payload

    def __generate_password(self):
        special_characters = string.punctuation
        digits = string.digits
        uppercase_letters = string.ascii_uppercase
        lowercase_letters = string.ascii_lowercase

        # Create a pool of characters
        pool = special_characters + digits + uppercase_letters + lowercase_letters

        # Ensure at least one character of each type
        password = random.choice(special_characters)
        password += random.choice(digits)
        password += random.choice(uppercase_letters)
        password += random.choice(lowercase_letters)

        # Fill the remaining length with random characters
        password += ''.join(random.choice(pool) for _ in range(20 - 4))

        # Shuffle the characters to make the password more random
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)

        return password

    def get_groups(self) -> pd.DataFrame:
        """
        Get all groups from Azure Entra
        :return: pd.DataFrame with the groups
        """
        endpoint = "https://graph.microsoft.com/v1.0"
        df = pd.DataFrame()
        loop = True
        url = f"{endpoint}/groups"
        while loop:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            groups = response.json()['value']
            df_temp = pd.json_normalize(groups)
            df = pd.concat([df, df_temp], ignore_index=True)
            if '@odata.nextLink' in response.json():
                url = response.json()['@odata.nextLink']
            else:
                loop = False
        df = df.reset_index(drop=True)
        return df

    def get_group_members(self, group_id: str = '') -> pd.DataFrame:
        """
        Get all users from a group in Azure Entra
        :param group_id: ID of the group. If no ID is given, all possible groups will be returned
        :return: pd.DataFrame with the users
        """
        group_url = "https://graph.microsoft.com/v1.0/groups/"
        df = pd.DataFrame()
        while group_url:
            graph_r = requests.get(group_url, headers=self.headers, timeout=self.timeout)
            graph_json = graph_r.json()
            groups = graph_json.get('value')
            for group in groups:
                print(f"Group ID: {group['id']}, Group Name: {group['displayName']}")
                # Get users in each group
                next_url_members = f"https://graph.microsoft.com/v1.0/groups/{group['id']}/members"
                while next_url_members:
                    members_r = requests.get(next_url_members, headers=self.headers, timeout=self.timeout)
                    members_json = members_r.json()
                    members = members_json.get('value')
                    df_temp = pd.json_normalize(members)
                    if len(df_temp) > 0:
                        df_temp['group_id'] = group['id']
                        df_temp['group'] = group['displayName']
                        df_temp.rename(columns={'id': 'user_id'}, inplace=True)
                        df = pd.concat([df, df_temp], ignore_index=True)
                    next_url_members = members_json.get('@odata.nextLink')
            group_url = graph_json.get('@odata.nextLink')

        df = df.reset_index(drop=True)
        return df

    def create_group(self, name: str = '', description: str = '', mail_enabled: bool = False, mail_nickname: str = '', security_enabled: bool = True):
        """
        Create a new group in Azure Entra
        :param name: Name of the group
        :param description: Description of the group
        :param mail_enabled: Is the group mail enabled?
        :param mail_nickname: Mail nickname of the group
        :param security_enabled: Is the group security enabled?
        :return: Response of the request
        """
        endpoint = "https://graph.microsoft.com/v1.0/groups"
        payload = {
            "displayName": f"{name}",
            "description": f"{description}",
            "mailEnabled": mail_enabled,
            "mailNickname": f"{mail_nickname}",
            "securityEnabled": security_enabled
        }
        response = requests.post(endpoint, headers=self.headers, json=payload, timeout=self.timeout)
        return response

    def update_group(self, id: int, name: str = '', description: str = '', mail_enabled: bool = False, mail_nickname: str = '', security_enabled: bool = True):
        """
        Create a new group in Azure Entra
        :param id: ID of the group
        :param name: Name of the group
        :param description: Description of the group
        :param mail_enabled: Is the group mail enabled?
        :param mail_nickname: Mail nickname of the group
        :param security_enabled: Is the group security enabled?
        :return: Response of the request
        """
        endpoint = f"https://graph.microsoft.com/v1.0/groups/{id}"
        payload = {
            "displayName": f"{name}",
            "description": f"{description}",
            "mailEnabled": mail_enabled,
            "mailNickname": f"{mail_nickname}",
            "securityEnabled": security_enabled
        }
        response = requests.patch(endpoint, headers=self.headers, json=payload, timeout=self.timeout)
        return response

    def delete_group(self, group_id):
        """
        Delete a group in Azure Entra
        :param group_id: ID of the group
        :return: Response of the request
        """
        endpoint = f"https://graph.microsoft.com/v1.0/groups/{group_id}"
        response = requests.delete(endpoint, headers=self.headers, timeout=self.timeout)
        return response

    def get_users(self, extra_fields: list = [], custom_attributes: bool = False, expand: str = '', expand_select: str = '') -> pd.DataFrame:
        """
        Get all users from Azure Entra
        :param extra_fields: Besided the default fields, you can add extra fields to the request. Put them in a list
        :param custom_attributes: Get the custom attributes of the users. If True, all the custom attributes will be returned
        :return: pd.DataFrame with the users
        """
        fields = ['businessPhones', 'displayName', 'givenName', 'id', 'jobTitle', 'mail', 'mobilePhone',
                  'officeLocation', 'preferredLanguage', 'surname', 'userPrincipalName'] + extra_fields
        fields = ','.join(fields)
        endpoint = f"https://graph.microsoft.com/v1.0/users?$select={fields}"
        if custom_attributes:
            endpoint = f"https://graph.microsoft.com/beta/users?$select={fields},customSecurityAttributes"
            # Adding expand and select parameters if provided
        if expand:
            if expand_select:
                endpoint += f",&$expand={expand}($select={expand_select})"
            else:
                endpoint += f",&$expand={expand}"

        df = pd.DataFrame()
        while endpoint:
            response = requests.get(endpoint, headers=self.headers, timeout=self.timeout)
            endpoint = response.json().get('@odata.nextLink')
            data = response.json().get('value')
            df_temp = json_normalize(data, sep='.')
            df_temp = df_temp.drop([col for col in df_temp.columns if 'odata.type' in col], axis=1)
            df = pd.concat([df, df_temp], ignore_index=True)
        df = df.reset_index(drop=True)
        return df

    def create_user(self, account_enabled=True, display_name='', mail_nickname='', user_principal_name='', password='', force_change_password_next_sign_in=False, extra_fields={}, custom_attributes={}):
        """
        Create a new user in Azure Entra
        :param account_enabled: Is the account enabled? By default True
        :param display_name: Display name of the user
        :param mail_nickname: Mail nickname of the user (the part before the @)
        :param user_principal_name: User principal name of the user
        :param password: Password of the user. If no password is given, a random password will be generated
        :param force_change_password_next_sign_in: Force the user to change the password on the next sign in. By default False
        :param extra_fields: Extra fields you want to add to the user. Put them in a dictionary
        :param custom_attributes: A dictionary with the name of the custom attribute and the value. It could be multiple custom attributes
        """
        # Custom attributes are only available in the beta version of the API
        endpoint = 'https://graph.microsoft.com/beta/users' if custom_attributes else 'https://graph.microsoft.com/v1.0/users'
        if password == '':
            password = self.__generate_password()

        payload = {
            "accountEnabled": account_enabled,
            "displayName": f"{display_name}",
            "mailNickname": f"{mail_nickname}",
            "userPrincipalName": user_principal_name,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": force_change_password_next_sign_in,
                "password": f"{password}"
            },
        }
        payload.update(extra_fields)

        # If there are any custom attributes, add them to the payload. But since the endpoint needs extra metadata, we need to do some extra work
        if len(custom_attributes) > 0:
            payload = self.__add_attribute_information(payload, custom_attributes)
        response = requests.post(endpoint, headers=self.headers, json=payload, timeout=self.timeout)
        return response

    def update_user(self, user_id, fields_to_update: dict = {}, custom_attributes: dict = {}, update_password: bool = False):
        """
        Update a user in Azure Entra
        :param user_id: The Azure AD ID of the user
        :param fields_to_update: A dictionary with the fields you want to update. Don't put the custom attributes in this dictionary
        :param custom_attributes: A dictionary with the name of the custom attribute and the value. It could be multiple custom attributes
        :param update_password: If True, the password will be updated with a random value. If False, the password will not be updated
        """
        endpoint = f'https://graph.microsoft.com/beta/users/{user_id}' if len(custom_attributes) > 0 else f'https://graph.microsoft.com/v1.0/users/{user_id}'
        payload = fields_to_update
        if update_password:
            password = self.__generate_password()
            payload.update({"passwordProfile": {
                "forceChangePasswordNextSignIn": False,
                "password": f"{password}"
            }})
        if len(custom_attributes) > 0:
            payload = self.__add_attribute_information(payload, custom_attributes)
        response = requests.patch(endpoint, headers=self.headers, json=payload, timeout=self.timeout)
        return response

    def delete_user(self, user_id, delete=False):
        """
        Delete (soft or hard) a user from Azure Entra
        :param user_id: The Azure AD ID of the user
        :param delete: If True, the user will be deleted permanently. If False, the user will be soft deleted
        """
        endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}"
        if delete:
            response = requests.delete(endpoint, headers=self.headers, timeout=self.timeout)
        else:
            payload = {"accountEnabled": False}
            response = requests.patch(endpoint, headers=self.headers, data=json.dumps(payload), timeout=self.timeout)
        return response

    def assign_user_to_group(self, user_id, group_id):
        """
        Assign a user to a group
        :param user_id: The Azure AD ID of the user
        :param group_id: The Azure AD ID of the group
        return: response
        """
        url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref"
        data = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"}
        response = requests.post(url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)
        return response

    def update_manager(self, user_id, manager_id):
        """
        Update the manager of a user
        :param user_id: The Azure AD ID of the user
        :param manager_id: The Azure AD ID of the manager
        return: response
        """
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/manager/$ref"
        content ={f"@odata.id": f"https://graph.microsoft.com/v1.0/users/{manager_id}"}
        response = requests.put(url, headers=self.headers, data=json.dumps(content), timeout=self.timeout)
        return response

    def remove_user_from_group(self, user_id, group_id):
        """
        Remove a user from a group
        :param user_id: The Azure AD ID of the user
        :param group_id: The Azure AD ID of the group
        return: response
        """
        url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/{user_id}/$ref"
        response = requests.delete(url, headers=self.headers, timeout=self.timeout)
        return response
