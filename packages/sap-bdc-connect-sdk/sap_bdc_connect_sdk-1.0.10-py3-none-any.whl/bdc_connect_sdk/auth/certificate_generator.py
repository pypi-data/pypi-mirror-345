# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID

class CertificateGenerator:
    def generate_self_signed_certificate(self, workspace_url):
        one_day = datetime.timedelta(1, 0, 0) # 1 day
        expiration_days = datetime.timedelta(15, 0, 0) # 15 days
        
        private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend())
        public_key = private_key.public_key()

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, workspace_url)]))
        builder = builder.issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, workspace_url)]))
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.today() + expiration_days)
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(public_key)
        builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        
        certificate = builder.sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
        )

        cert = certificate.public_bytes(serialization.Encoding.PEM)
        key = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )

        cert_file = "_sap_bdc_connect_sdk_cert.crt"
        key_file = "_sap_bdc_connect_sdk_cert.key"

        with open(cert_file, "wb") as f:
            f.write(cert)

        with open(key_file, "wb") as f:
            f.write(key)

        return (cert, key)

# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
