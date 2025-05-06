# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
import requests
import hashlib
import base64
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from bdc_connect_sdk.auth.certificate_generator import CertificateGenerator 
 
class DatabricksClient:
    def __init__(self, dbutils) -> None:
        self.dbutils = dbutils
        
    def get_id_token(self): 
        databricks_workspace_url = self.dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().getOrElse(None) 
        databricks_api_token = self.dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None) 
        endpoint = '/oidc/v1/token'
        audience = self.get_secret("token_audience")
        
        cert_pem, _ = CertificateGenerator().generate_self_signed_certificate(databricks_workspace_url)

        cert = load_pem_x509_certificate(cert_pem, default_backend())
        
        certificate_der = cert.public_bytes(encoding=serialization.Encoding.DER)

        hash_sha256 = hashlib.sha256(certificate_der).digest()
        hash_base64_urlsafe = base64.urlsafe_b64encode(hash_sha256).decode('utf-8').rstrip('=')

        payload = { 
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange', 
            'subject_token': databricks_api_token, 
            'subject_token_type': 
    'urn:databricks:params:oauth:token-type:personal-access-token', 
            'requested_token_type': 'urn:ietf:params:oauth:token-type:id_token', 
            'scope': 'openid profile email', 
            'audience': audience,
            'cnf_x5t_sha256': hash_base64_urlsafe
        }
        
        return requests.post(databricks_workspace_url + endpoint, data=payload).json().get('id_token')
    
    def get_secret(self, secret): 
        return self.dbutils.secrets.get("sap-bdc-connect-sdk", secret)

# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
