#!/usr/bin/env python

import json

from fake_reviews import createReview

TOT_SAMPLES = 100000

if __name__ == '__main__':

    series = {}

    for idx in range(TOT_SAMPLES):
        msg = createReview(idx)
        #
        try:
            rev = json.loads(msg)
            uid = rev.get('u_id', rev.get('user_id'))
            tgt = rev['item_name']
            pair = (tgt, uid)
            series[pair] = series.get(pair, []) + [(idx, rev['score'])]
        except Exception:
            pass

    # we print the files
    for (tgt, uid), ser in series.items():
        with open('test_data/%s_%s.dat' % (tgt.replace(' ', '-'), uid), 'w') as f:
            f.write('%s\n' % (
                '\n'.join(
                    '%i\t%f' % (x, y)
                    for x, y in ser
                )
            ))

    # gnuplot commands (heh)
    tgts = {t for t, _ in series.keys()}
    for tgt in tgts:
        uids = {u for t, u in series.keys() if t == tgt}
        print('\nplot %s' % (
            ', '.join(
                '\'%s\' u 1:2 w po t \'%s\'' % (
                    '%s_%s.dat' % (tgt.replace(' ', '-'), uid),
                    '%s (%s)' % (tgt, uid)
                )
                for uid in sorted(uids)
            )
        ))
