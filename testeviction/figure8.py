"""
Monte-Carlo simulation:
eclipse probability for test-before-evict.
"""

import collections
import random
from random import randrange
import math
import matplotlib.pyplot as plt


def triedprob(rho, omega):
    """Probability an IP is seeded from the tried table.

    :param rho: (float) proportional size of tried table to new table.
    :param omega: (float) number of connected outgoing peers
    """
    rho_freq = math.sqrt(rho) * (9 - omega)
    return rho_freq / (1 + omega + rho_freq)


def sampleips(a, h, tablesize=4096):
    """Samples the IP to place in a given table cell.

    :param a: (int) attacker IPs
    :param h: (int) honest IPs
    :param tablesize: (int) the size of the tried table
    :return: yields a stream of (bucket, slot) => IP
    """
    p_attacker = float(a) / (a + h + tablesize)
    p_honest = float(h) / (a + h + tablesize)
    p_nonempty = p_attacker + p_honest
    n = max(a, h)
    for _ in range(n):
        r = random.random()
        if r <= p_attacker:
            bucket = randrange(64)
            slot = randrange(64)
            yield (bucket, slot), attacker
        elif r <= p_nonempty:
            bucket = randrange(64)
            slot = randrange(64)
            yield (bucket,slot), honest


def jointsample(n, *params):
    for _ in range(n):
        yield tuple(map(lambda e: random.choice(e), params))


random.seed(420)  # seed the random number generator to something... **sigh**.

N = 10000	 # num of sims
colors = ('red', 'orange', 'yellow', 'green')
P = (.8, .6, .4, .2)  # churn rate
ai = 30000 / 1000
hi = 2500 / 250
A = [round(ai * x) for x in range(26)]	 # attack IP  [0...30000]
H = [round(hi * x) for x in range(20)]	 # honest IP  [0...2500]
graph = {p: collections.defaultdict(int) for p in P}  # scatter plot

honest = 0
attacker = 1

for n in range(N):
    print("trial %d/%d" % (n+1, N))
    for h, p, a in jointsample(H, P, A):
        # table of outgoing connections from the victim
        outgoing = 0

        # Matrix of all IP adresses in tried table initialized to index in table
        # triedTable = dict()
        triedTable = {(bucket, slot): ip for (bucket, slot), ip in sampleips(a, h)}

        # insert honest in random posions of tried table
        # for _ in range(h):
        #     # 0 represents honest IP
        #     bucket = randrange(0,64)
        #     slot = randrange(0,64)
        #     triedTable[bucket, slot] = honest
        #
        # # insert attacker IPs into tried Table
        # for _ in range(a):
        #     # 1 represents attack IP
        #     bucket = randrange(0,64)
        #     slot = randrange(0,64)
        #     triedTable[bucket, slot] = attacker

        # fill outgoing connections table
        while outgoing < 8:
            omega = outgoing
            rho = len(triedTable) / 16384.
            # if tried is selected
            if random.random() <= triedprob(rho, omega):
                # append random IP from tried table
                bucket, slot = random.choice(list(triedTable.keys()))
                tempIP = triedTable[bucket, slot]
                if tempIP == honest:
                    if random.random() <= p:
                        break  # attacker did not eclipse the node
                else:
                    outgoing += 1

            else:
                # append from new table (attacker IP)
                outgoing += 1

        if outgoing == 8:
            # the attacker wins
            graph[p][a, h] += 1


# create the plot
series = []
labels = []
for i, p in enumerate(P):
    print("plotting", p)
    points, _ = zip(*graph[p].items())  # unzip point and size
    points = sorted(points, key=lambda e: e[0])
    x, y = zip(*points)  # unzip (x, y) points
    series.append(plt.scatter(x, y, color=colors[i], marker='o'))
    labels.append('p=%d%%' % int(100 * p))
plt.legend(series, labels, loc='best')
plt.show()