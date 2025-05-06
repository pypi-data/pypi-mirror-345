# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
import json
import unittest
from unittest.mock import patch, MagicMock

from bdc_connect_sdk.auth.bdc_connect_client import BdcConnectClient

SHARE_NAME = "dummy_share_name"
CERT_PEM = """
-----BEGIN CERTIFICATE-----
MIIDEDCCAfigAwIBAgIUDc1a7sJsSgyMBm8KNWqmZq4HOrowDQYJKoZIhvcNAQEL
BQAwOTE3MDUGA1UEAwwuaHR0cHM6Ly9kYmMtY2IwM2FjMGUtNTYxZC5jbG91ZC5k
YXRhYnJpY2tzLmNvbTAeFw0yNTAzMTgxNTI3NTZaFw0zMDAzMTgxNTI3NTZaMDkx
NzA1BgNVBAMMLmh0dHBzOi8vZGJjLWNiMDNhYzBlLTU2MWQuY2xvdWQuZGF0YWJy
aWNrcy5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCsLWn0te//
vdkYl61QEWZ+SCmjDQBYi/FxlYkzMjkHmrc5nSf6DdGJkv1ZQr7pOyMGzV9I83Jf
AxohwwUdHYTDBGxB0LQuLCjKlkkkvbLnmWc64mRUuCRuYfixXQoK4DgOVzSkgHYP
5mGqfAnaUrExZytAZS4o4IVETqaAH0U6Pq1QXnEv64AfckQeYcmkIy9Sz2p6zy+M
8yKhYGGgiMK1svQ5aZ/PDpuwt4qWWRtzj0QFepXn30Q7rH/gQlzKVAIzuXTjC+Q/
HK+iFHfX3nt8vOMIgtEBgOBZfqLgpqovofwbRB8cbvQyUUI+IW05m2G4NaoLiAL6
ayw3spaAAwtXAgMBAAGjEDAOMAwGA1UdEwEB/wQCMAAwDQYJKoZIhvcNAQELBQAD
ggEBAH2OBxEvTuLEABVrJz7nc6ntGneDt+ofDNkeoQ5YOOE15QInt1Y0SrDNoM3M
w5CAYy1Op1HiGOQ5JofuS+S63znR+vx25XnbJUAcAmj8UVukx6v6mYvGUAmaPJWW
EyOFwFeGG1sWW1v/WElS/ywrgOXor30maJ9TtD/PjY96tPALjy1SUaF/lTtZtpUC
oXUyQfKxZVHf6dZJ1hmz8aUEHLDT91W7hT84mZ1zhFeiMej6SSEh8+4PK2lCSdcD
lgo2d6k6aJU/+uS2oIFPzNAVoOZgVaTpgo0kg1mNHo5srZ7BwK8WLXI4yYM+NTcH
dvLDABFvT9i9IyGCeo57WcdpWto=
-----END CERTIFICATE-----
"""
ACCESS_TOKEN = {
  "access_token": "dummy_jwt_token",
  "expires_in": 3600
}
HOST = "https://cfcselfsigned1.files.hdl.iota-hdl-hc-dev.dev-aws.hanacloud.ondemand.com"
TENANT = "cfcselfsigned1"
HEADER = {
  'X-SAP-FileContainer': TENANT,
  'Authorization': f'Bearer {ACCESS_TOKEN["access_token"]}'
}


class TestBdcConnectClient(unittest.TestCase):
  def setUp(self):
    self.dbx_client = MagicMock()
    
    secret_mapping = {
      "api_url": HOST,
      "tenant": TENANT
    }

    def mock_get_secret(secret_name):
      return secret_mapping.get(secret_name)

    self.dbx_client.get_secret.side_effect = mock_get_secret

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.create_or_update_share')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.get_access_token_with_id_token', return_value=ACCESS_TOKEN)
  def test_create_or_update_share(self, mock_get_token: MagicMock, mock_create_or_update_share: MagicMock):
    body = json.dumps({
      "type": "REMOTE_SHARE",
      "provider": {
        "type": "FEDERATION",
        "name": "databricks"
      },
      "@openResourceDiscoveryV1": {
        "title": SHARE_NAME,
        "shortDescription": f"This is {SHARE_NAME}",
        "description": "This demonstrates that shares can be created and published."
      }
    })
    
    with BdcConnectClient(self.dbx_client) as bdc_connect_client:
      bdc_connect_client.create_or_update_share(
        SHARE_NAME,
        body
      )

    mock_get_token.assert_called_once()
    mock_create_or_update_share.assert_called_once_with(SHARE_NAME, TENANT, body, _headers=HEADER)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.create_or_update_share_csn')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.get_access_token_with_id_token', return_value=ACCESS_TOKEN)
  def test_create_or_update_share_csn(self, mock_get_token: MagicMock, mock_create_or_update_share_csn: MagicMock):
    body = json.dumps({
      "definitions": {
        "default": {
          "kind": "context"
        }
      },
      "i18n": {},
      "meta": {
        "creator": "BDS CSN Aggregator 1.0",
        "flavor": "inferred",
        "share_name": SHARE_NAME
      }
    })
    
    with BdcConnectClient(self.dbx_client) as bdc_connect_client:
      bdc_connect_client.create_or_update_share_csn(
        SHARE_NAME,
        body
      )

    mock_get_token.assert_called_once()
    mock_create_or_update_share_csn.assert_called_once_with(SHARE_NAME, TENANT, body, _headers=HEADER)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.publish_data_product')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.get_access_token_with_id_token', return_value=ACCESS_TOKEN)
  def test_publish_data_product(self, mock_get_token: MagicMock, mock_publish_data_product: MagicMock):
    with BdcConnectClient(self.dbx_client) as bdc_connect_client:
      bdc_connect_client.publish_data_product(SHARE_NAME)

    mock_get_token.assert_called_once()
    mock_publish_data_product.assert_called_once_with(SHARE_NAME, TENANT, _headers=HEADER)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.delete_share')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.get_access_token_with_id_token', return_value=ACCESS_TOKEN)
  def test_delete_share(self, mock_get_token: MagicMock, mock_delete_share: MagicMock):
    with BdcConnectClient(self.dbx_client) as bdc_connect_client:
      bdc_connect_client.delete_share(SHARE_NAME)

    mock_get_token.assert_called_once()
    mock_delete_share.assert_called_once_with(SHARE_NAME, TENANT, False, _headers=HEADER)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.create_or_update_share')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.create_or_update_share_csn')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.publish_data_product')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.delete_share')
  @patch('bdc_connect_sdk.auth.bdc_connect_client.get_access_token_with_id_token', return_value=ACCESS_TOKEN)
  def test_cached_token(self, mock_get_token: MagicMock, mock_delete_share: MagicMock,  mock_publish_data_product: MagicMock,
mock_create_or_update_share_csn: MagicMock, mock_create_or_update_share: MagicMock):
    with BdcConnectClient(self.dbx_client) as bdc_connect_client:
      bdc_connect_client.create_or_update_share(SHARE_NAME, {})
      bdc_connect_client.create_or_update_share_csn(SHARE_NAME, {})
      bdc_connect_client.publish_data_product(SHARE_NAME)
      bdc_connect_client.delete_share(SHARE_NAME)

    mock_create_or_update_share.assert_called_once_with(SHARE_NAME, TENANT, {}, _headers=HEADER)
    mock_create_or_update_share_csn.assert_called_once_with(SHARE_NAME, TENANT, {}, _headers=HEADER)
    mock_publish_data_product.assert_called_once_with(SHARE_NAME, TENANT, _headers=HEADER)
    mock_delete_share.assert_called_once_with(SHARE_NAME, TENANT, False, _headers=HEADER)
    
    # Ensure that request to get not cached token was called just one time
    mock_get_token.assert_called_once()
    
    # Ensure that the token is indeed cached
    cached_token_info = bdc_connect_client.token_cache.get(SHARE_NAME)
    self.assertIsNotNone(cached_token_info, f"Token is not cached for Share(name={SHARE_NAME})")
    

# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
