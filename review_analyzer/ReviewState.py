from sentiment import textSentiment

class ReviewState(object):

    def __init__(self, rollingAlpha):
        self.alpha = rollingAlpha
        self.rollingAverages = {}
        self.userTrolliness = {}

    def addReview(self, review):
        """
            Also returns whether the review looks like an outlier or not
        """
        tgtName =   review['tgt_name']
        rScore =    review['r_score']
        uID =       review['user_id']
        rText =     review['r_text']
        # 1. "trolliness" check and update for user
        # i.e. sentiment from text "opposite to" score
        sentiment = textSentiment(rText)
        isTrollish = any([
            (sentiment > +0.1 and rScore < 4),
            (sentiment < -0.1 and rScore > 6),
        ])
        if uID not in self.userTrolliness:
            self.userTrolliness[uID] = {'den': 0, 'num': 0}
        self.userTrolliness[uID]['den'] += 1
        self.userTrolliness[uID]['num'] += 1 if isTrollish else 0
        #
        # we absorb this review in the rolling average in all cases ...
        if tgtName not in self.rollingAverages:
            self.rollingAverages[tgtName] = rScore
        else:
            self.rollingAverages[tgtName] = (
                self.alpha * rScore
                + (1-self.alpha)*self.rollingAverages[tgtName]
            )
        # ... but if we think it is an outlier we notify the caller
        # (who may then take appropriate measures)
        return abs(self.rollingAverages[tgtName] - rScore) > 3


    def averages(self):
        return self.rollingAverages

    def trollinesses(self):
        return {
            uID: trollInfo['num']/trollInfo['den']
            for uID, trollInfo in self.userTrolliness.items()
        }
