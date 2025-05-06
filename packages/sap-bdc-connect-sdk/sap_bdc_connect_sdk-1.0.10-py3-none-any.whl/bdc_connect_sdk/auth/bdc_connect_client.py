# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
import json
import requests
from datetime import datetime
from datetime import timedelta

import urllib

from bdc_connect_sdk.auth.databricks_client import DatabricksClient
from ..generated.api_client import ApiClient, Configuration
from ..generated.api.publish_api import PublishApi
from ..generated.models.put_share_response import PutShareResponse
from ..generated.models.object_info import ObjectInfo

class BdcConnectClient:
    def __init__(self, databricks_client: DatabricksClient) -> None:
        self.databricks_client = databricks_client
        self.host = databricks_client.get_secret("api_url")
        self.cfc = databricks_client.get_secret("tenant")
        self._publish_api_client = None
        self.token_cache = {}

    def __enter__(self) -> "BdcConnectClient":
        config = Configuration()
        config.host = self.host
        config.cert_file = "_sap_bdc_connect_sdk_cert.crt"
        config.key_file = "_sap_bdc_connect_sdk_cert.key"
        self._publish_api_client = PublishApi(ApiClient(configuration=config))
        return self

    def create_or_update_share(self, share_name: str, share_file_contents: str) -> PutShareResponse:
        return self._exec_request_with_token_exchange(self._publish_api_client.create_or_update_share, share_name, self.cfc, share_file_contents)

    def create_or_update_share_csn(self, share_name: str, csn_file_contents: str) -> None:
        return self._exec_request_with_token_exchange(self._publish_api_client.create_or_update_share_csn, share_name, self.cfc, csn_file_contents)

    def publish_data_product(self, share_name: str) -> None:
        return self._exec_request_with_token_exchange(self._publish_api_client.publish_data_product, share_name, self.cfc)

    def delete_share(self, share_name: str, drop_cascade: bool = False) -> ObjectInfo:
        return self._exec_request_with_token_exchange(self._publish_api_client.delete_share, share_name, self.cfc, drop_cascade)

    def __exit__(self, *args) -> None:
        pass

    def _get_access_token(self, share_name):
        current_time = datetime.now()
        
        token_cached = self.token_cache.get(share_name)

        if token_cached and token_cached['expires_at'] > current_time:
            return self.token_cache[share_name]['token']

        id_token = self.databricks_client.get_id_token()

        token_response = get_access_token_with_id_token(self.host, id_token, share_name, self.cfc)
        access_token = token_response['access_token']
        expires_in = token_response['expires_in']

        expires_at = current_time + timedelta(seconds=expires_in)

        self.token_cache[share_name] = {
            'token': access_token,
            'expires_at': expires_at
        }

        return access_token

    def _exec_request_with_token_exchange(self, request_function, share_name, *args):
        access_token = self._get_access_token(share_name)

        headers = {
            'X-SAP-FileContainer': self.cfc,
            'Authorization': f'Bearer {access_token}'
        }

        return request_function(share_name, _headers=headers, *args)

def get_access_token_with_id_token(url_base, id_token, share_name, tenant):
    endpoint = '/oauth2/token'

    headers = {
        'X-SAP-FileContainer': tenant,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    authorization_details = [{
        'resources': [{
                'name': 'catalog:share:' + share_name,
                'type': 'REMOTE_SHARE',
                'provider': {
                    'type': 'FEDERATION',
                    'name': 'databricks'
                }
        }],
        'privileges': [
            'create',
            'append',
            'delete'
        ]
    }]

    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'subject_token': id_token,
        'subject_token_type': 'urn:ietf:params:oauth:token-type:id_token',
        'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
        'authorization_details': json.dumps(authorization_details)
    }

    encoded_payload = urllib.parse.urlencode(payload)

    response = requests.post(
        url_base + endpoint,
        headers=headers,
        data=encoded_payload,
        cert=("_sap_bdc_connect_sdk_cert.crt", "_sap_bdc_connect_sdk_cert.key"),
        verify=True
    ).json()
    
    if 'access_token' not in response or 'expires_in' not in response:
        raise Exception(f"Received access_token from {url_base + endpoint} is not in the correct format: Missing ['access_token', 'expires_in'] attributes. Response: {response}")

    return response

# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
