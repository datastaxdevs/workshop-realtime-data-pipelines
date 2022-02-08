from revAnalyzer.sentiment import textSentiment

class ReviewState(object):

    def __init__(self, rollingAlpha, trollishSentThreshold,
                 trollishScoreMidregion, outlierDetectionDistance):
        self.alpha = rollingAlpha
        self.trollishSentThreshold = trollishSentThreshold
        self.trollishScoreBounds = (
            5 - trollishScoreMidregion/2,
            5 + trollishScoreMidregion/2,
        )
        self.outlierDetectionDistance = outlierDetectionDistance
        # this contains per-item rolling averages and other info
        self.targetMap = {}
        # this contains per-user updated info
        self.userMap = {}

    def addReview(self, review):
        """
            Also returns whether the review looks like an outlier or not
        """
        tgtName =   review['tgt_name']
        tgtID =     review['tgt_id']
        rScore =    review['r_score']
        uID =       review['user_id']
        rText =     review['r_text']
        # 1. "trolliness" check and update for user
        # i.e. sentiment from text "opposite to" score
        sentiment = textSentiment(rText)
        isTrollish = any([
            (sentiment > +self.trollishSentThreshold and rScore < self.trollishScoreBounds[0]),
            (sentiment < -self.trollishSentThreshold and rScore > self.trollishScoreBounds[1]),
        ])
        if uID not in self.userMap:
            self.userMap[uID] = {
                'hits': 0,
                'num_outliers': 0,
                'trollings': 0,
                'target_map': {},
            }
        self.userMap[uID]['hits'] += 1
        self.userMap[uID]['trollings'] += 1 if isTrollish else 0
        #
        if not isTrollish:
            # this is a valid review. Let's update this user's map
            self.userMap[uID]['target_map'][tgtID] = (
                1 + self.userMap[uID]['target_map'].get(tgtID, 0)
            )
            # we absorb this review in the rolling average
            if tgtID not in self.targetMap:
                self.targetMap[tgtID] = {
                    'average': rScore,
                    'num_outliers': 0,
                    'hits': 1,
                    'name': tgtName,  # let's assume it will never change
                }
            else:
                self.targetMap[tgtID]['average'] = (
                    self.alpha * rScore
                    + (1-self.alpha)*self.targetMap[tgtID]['average']
                )
            self.targetMap[tgtID]['hits'] += 1
            # ... but if we think it is an outlier we notify the caller
            # (who may then take appropriate measures)
            isOutlier = abs(self.targetMap[tgtID]['average'] - rScore) > self.outlierDetectionDistance
            # we also update the outlier counts (per-user and per-target)
            self.targetMap[tgtID]['num_outliers'] += 1 if isOutlier else 0
            self.userMap[uID]['num_outliers'] += 1 if isOutlier else 0
            #
            return isOutlier
        else:
            # not an 'outlier' if outright trolling
            return False

    def targetInfo(self):
        return self.targetMap

    def userInfo(self):
        return self.userMap
