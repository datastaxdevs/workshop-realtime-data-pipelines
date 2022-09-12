""" tools.py """

import os
import pulsar
from dotenv import load_dotenv

load_dotenv()

def getPulsarClient():
    """Specialization for Astra Streaming connection."""
    service_url = os.environ['BROKER_URL']
    token = os.environ['PULSAR_TOKEN']
    return pulsar.Client(service_url, authentication=pulsar.AuthenticationToken(token))

