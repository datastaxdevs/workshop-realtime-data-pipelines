#!/usr/bin/env python

import json
import itertools
import os
import pulsar
from ratelimiter import RateLimiter
from dotenv import load_dotenv

from fake_reviews import createReview

RATE_PER_SECOND = 10

MAX_NUM = 20     # None

load_dotenv()


if __name__ == '__main__':

    # init connection
    PULSAR_CLIENT_URL = os.environ['PULSAR_CLIENT_URL']
    TENANT = os.environ['TENANT']
    NAMESPACE = os.environ['NAMESPACE']
    RAW_TOPIC = os.environ['RAW_TOPIC']
    client = pulsar.Client(PULSAR_CLIENT_URL)
    streamingTopic = 'persistent://{tenant}/{namespace}/{topic}'.format(
        tenant=TENANT,
        namespace=NAMESPACE,
        topic=RAW_TOPIC,
    )
    producer = client.create_producer(streamingTopic)

    # loop and publish
    rLimiter = RateLimiter(max_calls=RATE_PER_SECOND, period=0.05)
    for idx in itertools.count():
        with rLimiter:
            msg = createReview(idx)
            #
            print('* %i ... ' % idx, end ='')
            producer.send(msg.encode('utf-8'))
            print('[%s]' % msg)
        if MAX_NUM is not None and idx >= MAX_NUM - 1:
            break
