import os
import sys
import pandas as pd
from typing import Union, List
import requests
import datetime
import json
from io import StringIO
import paramiko
from brynq_sdk_brynq import BrynQ

class SFTPInterface(BrynQ):

    def __init__(self, label: Union[str, List], local_file_directory: str, debug: bool = False):
        """
        For the full documentation, see: https://leapsome.zendesk.com/hc/en-us/articles/4414678642193-SFTP-integration-
        """
        super().__init__()
        self.username, self.private_key = self._set_credentials(label)
        self.local_file_directory = local_file_directory
        os.makedirs(self.local_file_directory, exist_ok=True)
        self.hostname = 'sftp.leapsome.com'
        self.upload_folder = '/incoming/'

    def _set_credentials(self, label):
        """
        Get the credentials from BrynQ and get the username and private key from there
        """
        credentials = self.get_system_credential(system='leapsome', label=label)
        username = credentials['leapsome_account_id']
        private_key_temp = credentials['ssh_private_key'].strip()
        private_key_temp = private_key_temp.replace('----- ', '-----\n')
        private_key_temp = private_key_temp.replace(' -----', '\n-----')
        private_key_temp = StringIO(private_key_temp)
        private_key = paramiko.RSAKey.from_private_key(private_key_temp)

        return username, private_key

    def upload_users(self, df):
        """
        Upload users to Leapsome SFTP. Setup SFTP on their side first.
        :param df: pandas dataframe with the actual user information.
        """
        mandatory_columns = ['Leapsome UserID', 'External ID', 'Firstname (optional)', 'Lastname (optional)', 'Title (optional)', 'Email / Username (mandatory)', 'Phone (including country code, e.g. +1 123 123 123)',
                             'Teams (optional, to add multiple teams, please separate by SEMICOLON)', 'Manager Email / Username (optional)',
                             'Additional Manager(s) Email / Username (optional, to add multiple additional managers, please separate by SEMICOLON)', 'Level (optional)', 'Hire date (optional)', 'Office Location',
                             'Termination date (optional)', 'Gender (optional, male/female/diverse)', 'Birthday (optional, DD-MM-YYYY)', 'Platform language', 'Status', 'Attachment Filenames (export only)',
                             'HRBP for users matching these criteria (export only)', 'Bonus', 'Salary', 'Salary: Pay band name', 'Salary: Compensation Ratio', 'Salary: Currency', 'Equity: Number of shares', 'Equity: Type',
                             'Equity: Exercise price', 'Equity: Share value(# of shares x price)', 'Equity: Grant start date (DD-MM-YYYY)', 'Equity: Vesting period (months)', 'Equity: Vesting cliff (months)',
                             'Equity: Vesting cadence (monthly, quarterly, annually)']
        columns = df.columns.tolist()
        for column in mandatory_columns:
            if column not in columns:
                raise ValueError(f'The column {column} is not part of the dataframe. Please add it to the dataframe')

        df = df[mandatory_columns].copy()
        filename = f"leapsome_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(f'{self.local_file_directory}/{filename}', index=False, engine='openpyxl')

        # Create SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.hostname, username=self.username, pkey=self.private_key)

        # Upload the file
        with ssh_client.open_sftp() as sftp:
            response = sftp.put(f'{self.local_file_directory}/{filename}', f'{self.upload_folder}{filename}')

        return response

