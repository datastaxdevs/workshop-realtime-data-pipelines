""" samplePlotter.py
        used only to generate the illustrations
"""

import matplotlib.pyplot as plt


def loadData(fName):
    # returns (xs, ys)
    with open(fName) as f:
        return list(zip(*(
            (int(l2.split(' ')[0]), float(l2.split(' ')[1]))
            for l2 in (
                l.strip().replace('\t', ' ')
                for l in f.readlines()
            )
            if l2 != ''
        )))


def decimate(xy, freq):
    x2 = [
        v
        for i, v in enumerate(xy[0])
        if i % freq == 0
    ]
    y2 = [
        v
        for i, v in enumerate(xy[1])
        if i % freq == 0
    ]
    return [x2, y2]


if __name__ == '__main__':
    #
    theory = {
        'gold_f': loadData('../revGenerator/sample_data/theo_gold_f.dat'),
        'pizzas': loadData('../revGenerator/sample_data/theo_pizzas.dat'),
    }
    data = {
        'anne': decimate(loadData('../revGenerator/sample_data/data_gold_f_anne.dat'), 5),
        'rita': decimate(loadData('../revGenerator/sample_data/data_gold_f_rita.dat'), 5),
    }
    average = {
        'gold_f': decimate(loadData('../revAnalyzer/sample_averages/avg_gold_f.dat'), 5),
    }

    #
    fig = plt.figure(figsize=(16, 11))
    plt.plot(*theory['gold_f'], '-', lw=3, color='purple', label='Golden Fork (real score)')
    plt.plot(*theory['pizzas'], '-', lw=1, color='#008000', label='PizzaSmile (real score)')
    plt.xlim((0, 120000))
    plt.ylim((0, 10))
    plt.title('"Real" restaurant quality over time')
    plt.xlabel('Message generation')
    plt.ylabel('Rating')
    plt.legend(loc='lower left')
    fig.savefig('01_real-values.png')
    fig.savefig('01_real-values.svg')
    plt.close(fig)

    fig = plt.figure(figsize=(16, 11))
    plt.plot(*theory['gold_f'], '-', lw=2, color='purple', label='Golden Fork (real score)')
    plt.plot(*theory['pizzas'], '-', lw=1, color='#008000', label='PizzaSmile (real score)')
    plt.plot(*data['anne'], '*', color='orange', label='Anne for Golden Fork')
    plt.plot(*data['rita'], 'h', color='red', label='Rita for Golden Fork')
    plt.plot(*theory['gold_f'], '-', lw=2, color='purple', label=None)
    plt.xlim((0, 120000))
    plt.ylim((0, 10))
    plt.title('Actual reviews being generated')
    plt.xlabel('Message generation')
    plt.ylabel('Rating')
    plt.legend(loc='lower left')
    fig.savefig('02_reviews.png')
    fig.savefig('02_reviews.svg')
    plt.close(fig)

    fig = plt.figure(figsize=(16, 11))
    plt.plot(*theory['gold_f'], '-', lw=1, color='purple', label='Golden Fork (real score)')
    plt.plot(*theory['pizzas'], '-', lw=1, color='#008000', label='PizzaSmile (real score)')
    plt.plot(*data['anne'], '*', color='orange', label='Anne for Golden Fork', alpha=0.5)
    plt.plot(*data['rita'], 'h', color='red', label='Rita for Golden Fork', alpha=0.5)
    plt.plot(*average['gold_f'], '-', lw=3, color='#0000C0', label='Golden Fork (moving average)')
    plt.plot(*theory['gold_f'], '-', lw=2, color='purple', label=None)
    plt.xlim((0, 120000))
    plt.ylim((0, 10))
    plt.title('Moving average from received reviews')
    plt.xlabel('Message generation')
    plt.ylabel('Rating')
    plt.legend(loc='lower left')
    fig.savefig('03_moving-average.png')
    fig.savefig('03_moving-average.svg')
    plt.close(fig)
