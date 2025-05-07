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

class APIInterface(BrynQ):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://api.leapsome.com/v1/api-docs/
        """
        super().__init__()
        self.timeout = 3600
        self.headers = self._set_credentials(label)


    def _set_credentials(self, label):
        """
        Get the credentials from BrynQ and get the username and private key from there
        """
        credentials = self.get_system_credential(system='leapsome-api', label=label)
        api_key = credentials['api_key']
        jwt_token = requests.get(f'https://api.leapsome.com/v1/token?secret={api_key}', timeout=self.timeout)
        jwt_token = jwt_token.json()['token']
        headers = {'Authorization': f'Bearer {jwt_token}'}
        return headers

    def get_goal_objectives(self, user_id: str = None, team_id: str = None, tag_id: str = None, type: str = None, search: str = None, state: str = None, limit: int = 100):
        """
        Fetches goal objectives from the Leapsome API.

        Parameters:
        user_id (str): The ID of the user. Default is None. select goals containing any of the userIds.
        team_id (str): The ID of the team. Default is None. select goals containing any of the teamIds.
        tag_id (str): The ID of the tag. Default is None. select goals containing all of the tagIds.
        type (str): The type of the goal. Can be 'company', 'team', or 'user'. Default is None.
        search (str): The search query. search on title, user name and team name fields. Special symbols must be URL-encoded. Search is performed on a whole value of a text field, without splitting it into words (e.g. search for ark will match Marketing).
        state (str): The state of the goal. Can be 'live', 'draft', or 'archived'. Default is None.
        limit (int): The maximum number of goals to fetch. Default is 100.

        Returns:
        df (DataFrame): A pandas DataFrame containing the fetched goal objectives.

        Raises:
        ValueError: If the provided type is not 'company', 'team', 'user', or None.
        ValueError: If the provided state is not 'live', 'draft', 'archived', or None.
        """
        # check if type is in company, team or user, else raise error
        if type not in [None, 'company', 'team', 'user']:
            raise ValueError('The type should be either company, team or user')
        # check if state is in live, draft or archived, else raise error
        if state not in [None, 'live', 'draft', 'archived']:
            raise ValueError('The state should be either live, draft or archived')
        df = pd.DataFrame()
        cursor = ''
        while True:
            url = f'https://api.leapsome.com/v1/goals?limit={limit}&cursor={cursor}'
            params = {'userId': user_id, 'teamId': team_id, 'tagId': tag_id, 'type': type, 'search': search, 'state': state}
            url += ''.join([f'&{k}={v}' for k, v in params.items() if v])
            response = requests.request("GET", url, headers=self.headers, timeout=self.timeout)
            data = response.json()['data']
            cursor = response.json()['meta']['cursor']
            df_temp = pd.json_normalize(data)
            df = pd.concat([df, df_temp])
            if not cursor:
                break

        # Since the objectives are split into objectives, key results and contributors, and you can have multiple key_results per objective, we need to split them
        df_key_results = df[['id', 'keyResults']].copy()
        df_key_results = df_key_results.explode('keyResults')
        df_key_results = pd.concat([df_key_results.drop(['keyResults'], axis=1), df_key_results['keyResults'].apply(pd.Series)], axis=1)
        df_key_results = df_key_results.drop(df_key_results.columns[-1], axis=1)
        df_key_results.reset_index(inplace=True, drop=True)
        metric_expanded = df_key_results['metric'].apply(pd.Series)
        df_key_results = df_key_results.join(metric_expanded, how='left', rsuffix='_metric')
        df_key_results = df_key_results.drop(columns=['metric', 0])

        # Same goes for contributors
        df_contributors = df[['id', 'contributors']].copy()
        df_contributors = df_contributors.explode('contributors')
        df_contributors = pd.concat([df_contributors.drop(['contributors'], axis=1), df_contributors['contributors'].apply(pd.Series)], axis=1)
        df_contributors = df_contributors.drop(df_contributors.columns[-1], axis=1)
        df_contributors.reset_index(inplace=True, drop=True)
        df_contributors.columns.values[1] = 'user_id'

        # And for tags
        df_tags = df[['id', 'tags']].copy()
        df_tags = df_tags.explode('tags')
        df_tags = pd.concat([df_tags.drop(['tags'], axis=1), df_tags['tags'].apply(pd.Series)], axis=1)
        df_tags = df_tags.drop(df_tags.columns[1], axis=1)
        df_tags.columns.values[0] = 'objective_id'
        df_tags = df_tags[df_tags['id'].notna()].copy()
        df_tags.reset_index(inplace=True, drop=True)

        df = df.drop(columns=['keyResults', 'contributors', 'tags'])

        return df, df_key_results, df_contributors, df_tags