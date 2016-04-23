"""
Plots the success of eclipse attacks.
"""


import eclipse.utils
from matplotlib import pyplot as plt


f_values = [i / 100. for i in range(101)]
colors = ('red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet')
tau_l_values = (1, 2, 4, 5, 10, 24, 48)
lines = [[0 for j in f_values] for i in tau_l_values]
f_prime = 8 / 64 ** 2

for i, tau_l in enumerate(tau_l_values):
    for j, f in enumerate(f_values):
        lines[i][j] = eclipse.utils.q(f, f_prime, .45, tau_l, n=10)

plt.title('Probability of Eclipsing Node')
plt.xlabel('Fraction of adverserial addresses in tried')
plt.ylabel('Pr[Eclipsing node]')
for i, line in enumerate(lines):
    plt.plot(f_values, line, color=colors[i], linewidth=2., label='time invested: %d (hrs)' % tau_l_values[i])
plt.legend(loc='lower right')
plt.savefig('../figures/figure-2.png')