#!/usr/bin/env python

import argparse
import sys
import atexit
import os
from dotenv import load_dotenv

from pulsarTools.tools import getPulsarClient


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
    client = getPulsarClient()
    #
    TENANT = os.environ['TENANT']
    NAMESPACE = os.environ['NAMESPACE']
    topicToRead = 'persistent://{tenant}/{namespace}/{topic}'.format(
        tenant=TENANT,
        namespace=NAMESPACE,
        topic=args.topic,
    )
    consumer = client.subscribe(topicToRead,
                                subscription_name=args.subscription)

    @atexit.register
    def close_pulsar():
        print('Closing Pulsar resources')
        consumer.close()
        client.close()

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
