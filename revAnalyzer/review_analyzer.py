#!/usr/bin/env python

import argparse
import sys
import json
import os
from dotenv import load_dotenv
import time
import atexit

from pulsarTools.tools import getPulsarClient
from revAnalyzer.ReviewState import ReviewState
from revAnalyzer.database.dataStorage import (initDB, updateReviewer,
                                              updateRestaurant, updateIdSet,
                                              insertRestaurantTime)

from revAnalyzer.settings import (
    ROLLING_AVERAGE_ALPHA,
    TROLLISH_S_THRESHOLD,
    TROLLISH_MIDREGION_WIDTH,
    OUTLIER_DISTANCE,
)


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
        description='Analyze restaurant reviews as they come'
    )
    parser.add_argument('-r', '--reviews', help='periodically report reviews', action='store_true', default=False)
    parser.add_argument('-t', '--trolls', help='periodically report troll scores', action='store_true', default=False)
    parser.add_argument('-o', '--outliers', help='report outlier reviews as they come', action='store_true', default=False)
    parser.add_argument('-f', '--frequency', help='frequency of flushing/reporting (message count)', type=int, default=200)
    parser.add_argument('-l', '--latencyseconds', help='max time between DB flushes', type=int, default=180)
    args = parser.parse_args()
    #
    client = getPulsarClient()
    #
    TENANT = os.environ['TENANT']
    NAMESPACE = os.environ['NAMESPACE']
    INPUT_TOPIC = os.environ['RESTAURANT_TOPIC']
    ANOMALIES_TOPIC = os.environ['ANOMALIES_TOPIC']
    #
    initDB()
    #
    inputTopic = 'persistent://{tenant}/{namespace}/{topic}'.format(
        tenant=TENANT,
        namespace=NAMESPACE,
        topic=INPUT_TOPIC,
    )
    consumer = client.subscribe(inputTopic,
                                subscription_name='review-analyzer')
    #
    anomaliesTopic = 'persistent://{tenant}/{namespace}/{topic}'.format(
        tenant=TENANT,
        namespace=NAMESPACE,
        topic=ANOMALIES_TOPIC,
    )
    outlierProducer = client.create_producer(anomaliesTopic)

    @atexit.register
    def close_pulsar():
        print('Closing Pulsar resources')
        consumer.close()
        client.close()

    # Here we keep state (variables in this process, but may be a Redis or so!)
    reviewState = ReviewState(
        rollingAlpha=ROLLING_AVERAGE_ALPHA,
        trollishSentThreshold=TROLLISH_S_THRESHOLD,
        trollishScoreMidregion=TROLLISH_MIDREGION_WIDTH,
        outlierDetectionDistance=OUTLIER_DISTANCE,
    )

    # we basically keep consuming and update our internal state here,
    # handing out updates now and then.
    numReceived = 0
    receivedSinceDBFlush = 0
    lastMsgIdx = 0
    lastDBFlushTime = time.time()
    while True:
        msg = receiveOrNone(consumer, 50)
        if msg:
            numReceived += 1
            receivedSinceDBFlush += 1
            msgBody = json.loads(msg.data().decode())
            lastMsgIdx = msgBody['idx']

            # let's submit this review to the rolling state
            # (and get notified of whether-outlier as well)
            isOutlier = reviewState.addReview(msgBody)
            #
            if isOutlier:
                # print on screen
                outlierMessage = {k: v for k, v in msgBody.items()}
                outlierMessage['detected_by'] = 'review_analyzer.py'
                outlierProducer.send(json.dumps(outlierMessage).encode('utf-8'))
            #
            if args.outliers and isOutlier:
                print('[%6i] Outlier detected: "%s" on "%s" (rev %0.2f != avg %0.2f)' % (
                    lastMsgIdx,
                    msgBody['user_id'],
                    msgBody['tgt_name'],
                    msgBody['r_score'],
                    reviewState.targetInfo()[msgBody['tgt_id']]['average'],
                ))
            if numReceived % args.frequency == 0:
                # console output if required
                # Note we print the last message idx
                # and not the reception count here (to compare with input)
                if args.reviews:
                    print('[%6i] Restaurant Score Summary:\n%s' % (
                        lastMsgIdx,
                        '\n'.join(
                            '                 [%s %6i]   %-18s : %0.2f   (outliers: %6i/%6i)' % (
                                k,
                                msgBody['idx'],
                                '"%s"' % v['name'],
                                v['average'],
                                v['num_outliers'],
                                v['hits'],
                            )
                            for k, v in sorted(reviewState.targetInfo().items())
                        )
                    ))
                if args.trolls:
                    print('[%6i] Reviewer Summary:\n%s' % (
                        lastMsgIdx,
                        '\n'.join(
                            '                 %8s %6i : troll-score = %0.2f (outliers: %6i / %6i). Visits: %s' % (
                                '"%s"' % k,
                                msgBody['idx'],
                                v['trollings'] / v['hits'],
                                v['num_outliers'],
                                v['hits'],
                                ', '.join('%s(%i)' % (tk, tv) for tk, tv in sorted(v['target_map'].items())),
                            )
                            for k, v in sorted(reviewState.userInfo().items())
                        )
                    ))
            #
            consumer.acknowledge(msg)
        # regardless whether new messages right now or not,
        # we may want to flush to DB
        tooLongElapsed = (time.time() - lastDBFlushTime >= args.latencyseconds) and receivedSinceDBFlush > 0
        manyItemsPiledUp = receivedSinceDBFlush >= args.frequency
        if tooLongElapsed or manyItemsPiledUp:
            print('[%6i] Writing to DB ... ' % lastMsgIdx, end='')
            # persist latest values to DB
            restaurantMap = reviewState.targetInfo()
            reviewerMap = reviewState.userInfo()
            updateIdSet('restaurant', restaurantMap.keys())
            updateIdSet('reviewer', reviewerMap.keys())
            for revID, revInfo in reviewerMap.items():
                updateReviewer(
                    revID,
                    **revInfo,
                )
            for resID, resInfo in restaurantMap.items():
                updateRestaurant(
                    resID,
                    **resInfo,
                )
                insertRestaurantTime(
                    resID,
                    name=resInfo['name'],
                    average=resInfo['average'],
                )
            receivedSinceDBFlush = 0
            lastDBFlushTime = time.time()
            print('done.')
