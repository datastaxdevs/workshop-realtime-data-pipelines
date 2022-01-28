#!/usr/bin/env python

import pulsar
import argparse
import sys
import os
from dotenv import load_dotenv


TOPIC = 'rr-hotel-reviews'
# TOPIC = 'rr-restaurant-reviews'

load_dotenv()


def receiveOrNone(consumer, timeout):
    """
    A modified 'receive' function for a Pulsar topic
    that handles timeouts so that when the topic is empty
    it simply returns None.
    """
    try:
        msg = consumer.receive(timeout)
        return msg
    except Exception as e:
        if 'timeout' in str(e).lower():
            return None
        else:
            raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Read messages from a topic'
    )
    parser.add_argument('-t', '--topic', help='topic name')
    parser.add_argument('-s', '--subscription', help='subscription name', default='my-sub')
    parser.add_argument('-n', '--number', help='max number of messages', default=None, type=int)
    args = parser.parse_args()
    #
    PULSAR_CLIENT_URL = os.environ['PULSAR_CLIENT_URL']
    client = pulsar.Client(PULSAR_CLIENT_URL)
    consumer = client.subscribe(args.topic,
                                subscription_name=args.subscription)

    numReceived = 0
    while True:
        msg = receiveOrNone(consumer, 5000)
        if msg:
            numReceived += 1
            print("\n\n\t\tReceived message (%i): %s\n\n" % (numReceived, msg.data().decode()))
            consumer.acknowledge(msg)
        else:
            print('\n\n\tNOTHING RECEIVED\n\n')
        #
        if args.number is not None and args.number <= numReceived:
            break

    client.close()
