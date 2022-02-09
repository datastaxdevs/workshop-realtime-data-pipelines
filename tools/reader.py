#!/usr/bin/env python

import argparse
import sys
import atexit
import os
import json
import datetime
from dotenv import load_dotenv

from pulsarTools.tools import getPulsarClient


load_dotenv()


def _nowstr(): return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def _reindent(t, n): return '\n'.join('%s%s' % (' '*n, l) for l in t.split('\n'))


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
    parser.add_argument('-w', '--waitseconds', help='timeout for a single read', default=5.0, type=float)
    args = parser.parse_args()
    #
    client = getPulsarClient()
    #
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
        msg = receiveOrNone(consumer, int(args.waitseconds * 1000))
        if msg:
            numReceived += 1
            print('[%s] Received message %i:' % (_nowstr(), numReceived))
            msgContent = msg.data().decode()
            try:
                msgJson = json.loads(msgContent)
                print('    Type = JSON')
                print('%s\n' % _reindent(
                    json.dumps(msgJson, indent=4, sort_keys=True, ensure_ascii=False),
                    8,
                ))
            except Exception:
                print('    Type = RAW')
                print('        %s\n' % msgContent)
            #
            consumer.acknowledge(msg)
        else:
            print('[%s] ...' % _nowstr())
        #
        if args.number is not None and args.number <= numReceived:
            break
