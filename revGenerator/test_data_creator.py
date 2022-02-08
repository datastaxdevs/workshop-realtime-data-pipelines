#!/usr/bin/env python

import json
import math
import os

from revGenerator.fake_reviews import createReview, targets


outDir = 'sample_data'

numIterations = 120000
theoLineFrequency = 1000

if __name__ == '__main__':

    # item_id, u_id/user_id
    tracked = {
        ('gold_f', 'anne'),
        ('gold_f', 'rita'),
    }
    # theoretical scores: a map target_id -> (W, Phi)
    targetParams = {
        tgt[0]: (tgt[3], tgt[4])
        for tgt in targets
    }
    theoreticals = {'gold_f', 'pizzas'}
    def _theo(w, phi): return 5 + 4.5 * math.cos(idx*w + phi)

    # open files
    dataFiles = {
        k: open(
            os.path.join(
                outDir,
                'data_%s_%s.dat' % k,
            ),
            'w',
        )
        for k in tracked
    }
    theoFiles = {
        k: open(
            os.path.join(
                outDir,
                'theo_%s.dat' % k,
            ),
            'w',
        )
        for k in theoreticals
    }

    for idx in range(numIterations):
        msg = createReview(idx)
        #
        try:
            rev = json.loads(msg)
            uid = rev.get('u_id', rev.get('user_id'))
            tgt = rev['item_id']
            pair = (tgt, uid)
            if pair in dataFiles:
                dataFiles[pair].write('%i\t%.2f\n' % (
                    idx,
                    rev['score'],
                ))
        except Exception:
            pass
        #
        if idx % theoLineFrequency == 0:
            for k, f in theoFiles.items():
                theoVal = _theo(*targetParams[k])
                f.write('%i\t%.2f\n' % (
                    idx,
                    theoVal,
                ))

    #
    for f in dataFiles.values():
        f.close()
    for f in theoFiles.values():
        f.close()
