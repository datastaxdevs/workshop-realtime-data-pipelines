termSentiment = {
    'disgusting':   -1,
    'terrible':     -1,
    'horrible':     -1,
    #
    'good':         +1,
    'tasty':        +1,
    'excellent':    +1,
    'delicious':    +1,
}


def textSentiment(txt):
    # return a score in [-1,+1]
    # TOY IMPLEMENTATION! (aka don't use in prod :)
    words = txt.split(' ')
    score0 = sum(
        termSentiment.get(w, 0)
        for w in words
    ) / len(words)
    fullSentScore = min(1, max(-1, 2*score0))
    #
    return fullSentScore
