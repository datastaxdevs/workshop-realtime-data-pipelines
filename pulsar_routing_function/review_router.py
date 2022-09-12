from pulsar import Function
import json

DST_TOPIC_MAP = {
    'hotel':        'persistent://___TENANT___/default/rr-hotel-reviews',
    'restaurant':   'persistent://___TENANT___/default/rr-restaurant-reviews',
}

class ReviewRouter(Function):

    def __init__(self):
        pass

    def process(self, input_bytes, context):
        #
        logger = context.get_logger()
        #
        try:
            inputDict = json.loads(input_bytes)
        except:
            # we assume input was unreadable gibberish and we ignore it
            logger.warn('Gibberish text discarded')
            return

        #
        reviewType = inputDict.get('review_type')
        if reviewType is None:
            # we discard a review about unspecified-type targets
            logger.warn('No review type found')
            return
        else:
            # we proceed: normalize/transform and re-route the review
            userId = inputDict.get('user_id', inputDict.get('u_id'))
            score = inputDict['score']
            itemName = inputDict['item_name']
            itemID = inputDict['item_id']
            reviewText = inputDict['text']
            reviewIdx = inputDict['idx']
            #
            if reviewType in DST_TOPIC_MAP:
                outputDict = {
                    'user_id': userId,
                    'r_score': score,
                    'tgt_name': itemName,
                    'tgt_id': itemID,
                    'r_text': reviewText,
                    'idx': reviewIdx,
                }
                logger.info('Routing "%s" review to its topic' % reviewType)
                # All topics in this pipeline are schemaless, we JSON-encode:
                outMessage = json.dumps(outputDict).encode()
                context.publish(DST_TOPIC_MAP[reviewType], outMessage)
            else:
                # no destination topic configured
                logger.warn('No destination for this review type')
