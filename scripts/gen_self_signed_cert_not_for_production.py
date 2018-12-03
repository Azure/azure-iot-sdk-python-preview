#!/usr/bin/env python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

from datetime import datetime, timedelta

cert_file_name = "./certificate.pem"
key_file_name = "./key.pem"
passphrase = b"passphrase"

# Generate our key
key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
# Write our key to disk for safe keeping
with open("./key.pem", "wb") as f:
    f.write(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
        )
    )
# Various details about who we are. For a self-signed certificate the
# subject and issuer are always the same.
subject = issuer = x509.Name(
    [
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"WA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Redmond"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"ContosoDoNotUse"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"self-signed-do-not-use"),
    ]
)
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(
        # Our certificate will be valid for 10 days
        datetime.utcnow()
        + timedelta(days=10)
    )
    .add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
        # Sign our certificate with our private key
    )
    .sign(key, hashes.SHA256(), default_backend())
)

thumbprint = cert.fingerprint(hashes.SHA1()).hex()

# Write our certificate out to disk.
with open(cert_file_name, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Certificate:", cert_file_name)
print("Key:", key_file_name)
print("Thumbprint:", thumbprint)
