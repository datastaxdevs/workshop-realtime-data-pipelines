""" tools.py """

import os
import pulsar
from dotenv import load_dotenv

load_dotenv()

def getPulsarClient():
    """Specialization for Astra Streaming connection."""
    # Certificate location:
    # Mac (also need 'brew install libpulsar')
    # TRUST_CERTS = "/etc/ssl/cert.pem"
    # RHEL/CentOS:
    # TRUST_CERTS = '/etc/ssl/certs/ca-bundle.crt'
    # Debian/Ubuntu:
    TRUST_CERTS = '/etc/ssl/certs/ca-certificates.crt'
    #
    ASTRA_STREAMING_BROKER_URL = os.environ['ASTRA_STREAMING_BROKER_URL']
    ASTRA_STREAMING_TOKEN = os.environ['ASTRA_STREAMING_TOKEN']
    client = pulsar.Client(
        ASTRA_STREAMING_BROKER_URL,
        authentication=pulsar.AuthenticationToken(ASTRA_STREAMING_TOKEN),
        tls_trust_certs_file_path=TRUST_CERTS,
    )
    return client

