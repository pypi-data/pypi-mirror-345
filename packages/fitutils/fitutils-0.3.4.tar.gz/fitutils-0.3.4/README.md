# Fitutils

Function (and classes) to fit linear (either with intercept or not) model to data with normal uncertainties in *x* or *y* using Monte Carlo.

Optionnal plotting options are provided for convenience. Confidence interval (hull) is also calculated and optionnaly returned

Basic use:
``` Python
import numpy as np
import matplotlib.pyplot as plt
import fitutils as fu

N = 10
sx, sy = 1, 1
xx = np.arange(0, N, 1) + np.random.normal(0, sx, N)
yy = 2*xx + 3 + np.random.normal(0, sy, N)
dx = np.ones_like(xx) * sx
dy = np.ones_like(yy) * sy
```
Lets get the fit result and the confidence interval and plot them
``` Python
res, hull = fu.linfitxy(xx, yy, dx, dy, return_hull=True)
xl = np.arange(np.min(hull[0]), np.max(hull[0]), 0.1)
yl = res[0] * xl + res[1]

plt.figure()
plt.errorbar(xx, yy, xerr=dx, yerr=dy, fmt='o')
plt.plot(xl, yl, color='tab:orange')
plt.fill_between(hull[0], hull[1], hull[2], color='tab:orange', alpha=0.2)
plt.title(r'Fit: y = (' + '{:.{}f}'.format(res[0], 2) + ' $\pm$ '\
                        + '{:.{}f}'.format(res[2], 2) + ') x + ('\
                        + '{:.{}f}'.format(res[1], 1) + ' $\pm$ '\
                        + '{:.{}f}'.format(res[3], 1) + ')')
plt.show()
```
or more simply
``` Python
res = fu.linfitxy(xx, yy, dx, dy, plot=True)
print(res)
```
