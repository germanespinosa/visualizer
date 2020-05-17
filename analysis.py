import log_file
import sys
import matplotlib.pyplot as plt
import numpy as np


print(str(sys.argv[1]), str(sys.argv[2]))


experiment = log_file.LoadExperiment(str(sys.argv[1]))
baseline = log_file.LoadExperiment(str(sys.argv[2]))

x = np.arange(0, 10, 1)
ticks = np.arange(0, 10, 1)
y1 = np.zeros((len(x)))
y2 = np.zeros((len(x)))
xmax = 9
imax = 1
for ii in range(len(x)):
    y1[ii] = experiment["summary"][ii]["survival_rate"]
    y2[ii] = baseline["summary"][ii]["survival_rate"]
    ticks[ii] = ii / 9
ymax = max(y1)
fig = plt.figure(figsize=(8,4), dpi=300)
plt.plot(x, y1, 'g:')
plt.plot(x, y2, 'b:')
plt.ylim([0, ymax*1.05])
plt.xlim([0, xmax])
plt.fill_between(x, y1, y2, color='grey', alpha=0.3)
print (imax)
for ii in range(imax):
    plt.text(x[ii], ymax*0.01, ticks[ii])
plt.savefig(str(sys.argv[1]) + "_" + str(sys.argv[2]))
plt.show()
