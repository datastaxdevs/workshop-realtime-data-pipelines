import json
import time
import math
import random

from revGenerator.words import wordMap


NORMALOID_K = 1.4

targets = [
    ('gold_f', 'Golden Fork',     'restaurant',   0.00005, 0.5),
    ('pizzas', 'Pizza Smile',     'restaurant',   0.00007, 1.0),
    ('vegg00', 'VeggieParadise',  'restaurant',   0.00003, 1.5),
    ('slpsnd', 'SleepSound',      'hotel',        0.00004, 0.0),
    ('eat_st', 'EatNStay',        None,           0.00002, 0.0),
]


users = [
    ('john', 1.5, False),
    ('anne', 4.4, False),
    ('geri', 0.5, True),
    ('botz', 5.0, False),
    ('rita', 2.3, False),
]


def _normaloid(x, K):
    # K must be < PI/2. The closer it is = the sharper the peak
    # x uniform in [0:1], result is normaloid in [-1:1]
    return math.tan(K*(2*x-1))/math.tan(K)


def _pickRep(lst, n):
    return [
        lst[random.randint(0, len(lst) - 1)]
        for _ in range(n)
    ]


def _permute(lst):
    lst1 = []
    lst0 = [i for i in lst]
    while lst0 != []:
        idx = random.randint(0, len(lst0)-1)
        lst1 += [lst0[idx]]
        lst0 = lst0[:idx] + lst0[idx+1:]
    return lst1


def initRandom(seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(int(time.time()))


def makeText(score, trollish):
    if score < 3.5:
        tone = 'bad' if not trollish else 'good'
    elif score < 7.5:
        tone = 'neutral'
    else:
        tone = 'good' if not trollish else 'bad'
    #
    components0 = _pickRep(wordMap['neutral'], random.randint(2,6))
    components1 = _pickRep(wordMap[tone], random.randint(2,4))
    return ' '.join(_permute(components0 + components1))


def createReview(idx):
    isGibberish = random.random() < 0.05
    if isGibberish:
        return ''.join(
            chr(ord('0') + random.randint(0,50))
            for _ in range(random.randint(10,100))
        )
    else:
        # an actual JSON-encoded message
        # let's randomize it a bit for fun and profit
        uidFieldName = ['u_id', 'user_id'][random.randint(0, 1)]
        # pick target
        targetID, targetName, targetType, targetW, targetPhi = targets[
            random.randint(0, len(targets)-1)
        ]
        # pick user
        userId, userA, trollish = users[
            random.randint(0, len(users)-1)
        ]
        #
        score0 = 5 + 4.5 * math.cos(idx*targetW + targetPhi)
        score1 = score0 + userA*_normaloid(random.random(), NORMALOID_K)
        score2 = min(10, max(0, score1))
        score = 0.1 * int(10 * score2)
        # create review text (Note: very rough)
        reviewText = makeText(score, trollish)
        #
        return json.dumps({
            k: v
            for k, v in {
                uidFieldName: userId,
                'score': score,
                'review_type': targetType,
                'item_id': targetID,
                'item_name': targetName,
                'text': reviewText,
                'idx': idx,
            }.items()
            if v is not None
        })
