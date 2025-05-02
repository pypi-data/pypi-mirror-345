"""
Linfitxy V0.3.4
Dev: Marc-Antoine Verdier based on the Matlab version made by Julien
Browaeys and Tristan Beau: https://github.com/tjbtjbtjb/linfitxy

This module provides utilities for fitting data using linear regression
and curve fitting methods. It includes support for error propagation,
Monte Carlo simulations, and visualization of fit results.
"""
import numpy as np
import numpy.random as rd
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt
import scipy.optimize as opt
import scipy.special as spe
import scipy.stats as stats
import sys


def _val2str(nsig, val):
    """
    Convert a value to a string with a specified number of significant digits.

    Parameters:
        nsig (int): Number of significant digits.
        val (float): Value to format.

    Returns:
        str: Formatted string.
    """
    if nsig < 1:
        pre = -int(nsig - 2)
        return "{:.{}f}".format(val, pre)
    else:
        pre = 10**int(nsig)
        return "{:.0f}".format(np.round(val / pre) * pre)


def lin_title(p):
    """
    Generate a title string for a linear fit.

    Parameters:
        p (list): Fit parameters.

    Returns:
        str: Title string describing the fit equation.
    """
    if len(p) > 2:
        if p[2] != 0:
            nd0 = np.log10(p[2])
            fmt_s0 = _val2str(nd0, p[2])
            fmt_p0 = _val2str(nd0, p[0])
        else:
            nd0 = np.log10(p[0])
            fmt_p0 = _val2str(nd0, p[0])
            fmt_s0 = "0"
        if p[3] != 0:
            nd1 = np.log10(p[3])
            fmt_p1 = _val2str(nd1, p[1])
            fmt_s1 = _val2str(nd1, p[3])
        else:
            nd1 = np.log10(p[1])
            fmt_p1 = _val2str(nd0, p[1])
            fmt_s1 = "0"
        return f'Fit: y = ({fmt_p0} $\pm$ {fmt_s0}) x + ({fmt_p1} $\pm$ {fmt_s1}) '
    else:
        if p[1] != 0:
            nd0 = np.log10(p[1])
            fmt_s0 = _val2str(nd0, p[1])
            fmt_p0 = _val2str(nd0, p[0])
        else:
            nd0 = np.log10(p[0])
            fmt_p0 = _val2str(nd0, p[0])
            fmt_s0 = "0"
        return f'Fit: y = ({fmt_p0} $\pm$ {fmt_s0}) x'


def _sigxy(a, sx, sy):
    """
    Calculate the combined uncertainty for x and y errors.

    Parameters:
        a (float): Slope of the line.
        sx (float): Uncertainty in x.
        sy (float): Uncertainty in y.

    Returns:
        float: Combined uncertainty.
    """
    return np.sqrt((a*sx)**2 + sy**2 + sys.float_info.epsilon)


def gauss_quantiles(n_sigma=1):
    """
    Compute Gaussian quantiles for a given number of standard deviations.

    Parameters:
        n_sigma (float): Number of standard deviations.

    Returns:
        tuple: Upper and lower quantiles.
    """
    q_h = 0.5 * spe.erfc(n_sigma / np.sqrt(2))
    q_l = 1 - q_h
    return q_h, q_l


class Fitter(object):
    """
    Base class for fitting data.

    Attributes:
        func (callable): Function to fit.
    """

    def __init__(self, func):
        self.func = func

    def fit(self, data, p0=None, nb_loop=500):
        """
        Fit the data using the specified function.

        Parameters:
            data (Data): Data object containing x, y, and uncertainties.
            p0 (list): Initial guess for fit parameters.
            nb_loop (int): Number of Monte Carlo iterations.

        Returns:
            FitRes: Fit results.
        """
        pass


class LinFitXY(Fitter):
    """
    Linear fitting with x and y uncertainties.

    Methods:
        func_affine: Affine function (y = ax + b).
        func_linear: Linear function (y = ax).
    """

    @staticmethod
    def func_affine(x, a, b):
        return a*x + b

    @staticmethod
    def func_linear(x, a):
        return a*x

    def __init__(self, func):
        super().__init__(func)

    def fit(self, data, p0=None, nb_loop=500):
        """
        Perform linear fitting with error propagation.

        Parameters:
            data (Data): Data object containing x, y, and uncertainties.
            p0 (list): Initial guess for fit parameters.
            nb_loop (int): Number of Monte Carlo iterations.

        Returns:
            FitRes: Fit results.
        """

        @staticmethod
        def _affeq_err(p, x, y, sx, sy):
            return (y - p[0]*x - p[1]) / _sigxy(p[0], sx, sy)

        @staticmethod
        def _lineq_err(p, x, y, sx, sy):
            return (y - p[0]*x) / _sigxy(p[0], sx, sy)

        def _aff_fit_err(data):
            if p0 is not None:
                pt = p0
            else:
                # pt = poly.polyfit(data.x, data.y, deg=1, w=1/data.dy)
                pt = opt.least_squares(_affeq_err, [1, 1],
                                       args=(data.x, data.y, 0, data.dy)).x
            re = np.zeros((nb_loop, 2))
            for i in range(nb_loop):
                ag = (xloop[i], yloop[i], data.dx, data.dy)
                ls = opt.least_squares(_affeq_err, pt, args=ag)
                pt = ls.x
                re[i] = pt
            return re

        def _lin_fit_err(data):
            if p0 is not None:
                pt = p0
            else:
                pt = np.sum(data.y) / np.sum(data.x)
            re = np.zeros((nb_loop, 1))
            for i in range(nb_loop):
                ag = (xloop[i], yloop[i], data.dx, data.dy)
                ls = opt.least_squares(_lineq_err, pt, args=ag)
                pt = ls.x
                re[i] = pt
            return re

        rng = rd.default_rng()
        xloop = rng.normal(data.x, data.dx, (nb_loop, data.dx.shape[0]))
        yloop = rng.normal(data.y, data.dy, (nb_loop, data.dy.shape[0]))
        if self.func.__name__ == LinFitXY.func_affine.__name__:
            allpr = _aff_fit_err(data)
        elif self.func.__name__ == LinFitXY.func_linear.__name__:
            allpr = _lin_fit_err(data)
        return FitRes(self, data, allpr)


class CurveFitY(Fitter):
    """
    Curve fitting using scipy.optimize.curve_fit.

    Methods:
        fit: Perform curve fitting.
    """

    def __init__(self, func):
        super().__init__(func)

    def fit(self, data, p0=None, nb_loop=500):
        """
        Perform curve fitting.

        Parameters:
            data (Data): Data object containing x, y, and uncertainties.
            p0 (list): Initial guess for fit parameters.
            nb_loop (int): Number of Monte Carlo iterations.

        Returns:
            FitRes: Fit results.
        """
        popt, pcov = opt.curve_fit(self.func, data.x, data.y, p0=p0,
                                   sigma=data.dy, absolute_sigma=True)
        allpr = rd.default_rng().multivariate_normal(popt, pcov, nb_loop)
        return FitRes(self, data, allpr, popt, pcov)


class FitRes(object):
    """
    Class to store fit results and provide utilities for analysis and plotting.

    Attributes:
        popt (list): Optimal fit parameters.
        pcov (ndarray): Covariance matrix of fit parameters.
        chi2 (float): Chi-squared value of the fit.
        residus (ndarray): Residuals of the fit.
        residus_norm (ndarray): Normalized residuals.
        params (ndarray): Fit parameters with uncertainties.
    """

    def __init__(self, fitter, data, allpr, popt=None, pcov=None):
        self._fitter = fitter
        self._data = data
        self._allpr = allpr
        self.popt = popt
        self.pcov = pcov
        self._calc_params()

    def _calc_params(self):
        """
        Calculate fit parameters, uncertainties, and residuals.
        """
        q_h, q_l = gauss_quantiles(n_sigma=1)
        p_low = np.quantile(self._allpr, q_l, axis=0)
        p_hig = np.quantile(self._allpr, q_h, axis=0)
        if self.popt is None:
            self.popt = np.median(self._allpr, axis=0)
        if self.pcov is None:
            self.pcov = np.cov(self._allpr.T)
        s_l = np.abs(p_low - self.popt)
        s_h = np.abs(p_hig - self.popt)
        self.sig = np.mean([s_l, s_h], axis=0)
        if self._fitter.__class__.__name__ == 'LinFitXY':
            self._dy = _sigxy(self.popt[0], self._data.dx, self._data.dy)
        else:
            self._dy = self._data.dy
        self.chi2 = np.sum(
            (self._data.y - self._fitter.func(self._data.x, *self.popt))**2 / self._dy**2)
        self.residus = self._data.y - \
            self._fitter.func(self._data.x, *self.popt)
        self.residus_norm = self.residus / self._dy
        self.params = np.concatenate([self.popt, self.sig])

    def plot(self, xplot, style=None, draw_hull=True, marker='.',
             markercolor='tab:blue', linecolor='tab:orange',
             h_color=None, fill_between=True, title=None, grid=True, labels=None):
        """
        Plot the fit results.

        Parameters:
            xplot (ndarray): X values for plotting the fit curve.
            style (str): Plot style ('simple', 'residuals', or 'resnorm').
            draw_hull (bool): Whether to draw the uncertainty hull.
            marker (str): Marker style for data points.
            markercolor (str): Color of data points.
            linecolor (str): Color of the fit line.
            h_color (str): Color of the uncertainty hull.
            fill_between (bool): Whether to fill the uncertainty hull.
            title (str): Plot title.
            grid (bool): Whether to display a grid.
            labels (list): Axis labels.

        Returns:
            tuple: Figure and axes objects.
        """

        def _plot_datafit(ax):
            ax.errorbar(self._data.x, self._data.y, xerr=self._data.dx,
                        yerr=self._data.dy, fmt=marker, c=markercolor,
                        ecolor=markercolor)
            ax.plot(xplot, yplot, color=linecolor)
            if callable(title):
                ax.set_title(title(self.params))
            elif isinstance(title, str):
                ax.set_title(title)
            if draw_hull:
                if h_color is None:
                    h_color_ = linecolor
                if fill_between:
                    ax.fill_between(xplot, curve_[1], curve_[2],
                                    color=h_color_, alpha=0.35)
                else:
                    ax.plot(xplot, curve_[1], '--', color=h_color_)
                    ax.plot(xplot, curve_[2], '--', color=h_color_)

        curve_ = self.curve(xplot, return_hull=draw_hull, n_sigma=1)
        yplot = curve_[0] if draw_hull else curve_
        if style == True or style.lower() == 'simple':
            fig, ax = plt.subplots(1, 1)
            _plot_datafit(ax)
            if labels is not None:
                ax.set_xlabel(labels[0])
                ax.set_ylabel(labels[1])
        elif style.lower() == 'residuals':
            fig, ax = plt.subplots(2, 1, sharex=True, height_ratios=[2/3, 1/3])
            fig.subplots_adjust(hspace=0)
            _plot_datafit(ax[0])
            if labels is not None:
                ax[1].set_xlabel(labels[0])
                ax[0].set_ylabel(labels[1])
            ax[1].errorbar(self._data.x, self.residus,
                        #    xerr=self._data.dx,
                           yerr=self._dy,
                           fmt=marker, c=markercolor,
                           ecolor=markercolor)
            ax[1].axhline(0, color='black', lw=0.5)
            ax[1].set_ylabel('Residuals')
            ax[1].set_xlim(ax[0].get_xlim())
            if grid:
                ax[0].grid()
                ax[1].grid()
        elif style.lower() == 'resnorm':
            fig, ax = plt.subplot_mosaic([['data_pan', 'hist_pan'],
                                          ['resi_pan', 'hist_pan']],
                                         sharex=False,
                                         sharey=False,
                                         width_ratios=[2/3, 1/3],
                                         height_ratios=[2/3, 1/3],
                                         figsize=(6.4*1.5, 4.8))

            _x = np.linspace(-5, 5, 100)
            fig.subplots_adjust(hspace=0)
            _plot_datafit(ax['data_pan'])
            if labels is not None:
                ax['resi_pan'].set_xlabel(labels[0])
                ax['data_pan'].set_ylabel(labels[1])
            ax['data_pan'].set_ylabel('y')
            ax['resi_pan'].errorbar(self._data.x,
                                    self.residus,
                                    # xerr=self._data.dx,
                                    yerr=self._dy,
                                    fmt=marker,
                                    c=markercolor,
                                    ecolor=markercolor)
            ax['resi_pan'].axhline(0, color='black', lw=0.5)
            ax['resi_pan'].set_xlabel('x')
            ax['resi_pan'].set_ylabel('Residuals')
            ax['resi_pan'].set_xlim(ax['data_pan'].get_xlim())
            ax['hist_pan'].hist(
                self.residus_norm, bins='rice', density=True)
            ax['hist_pan'].plot(_x, stats.norm.pdf(_x),
                                label='$\mathcal{N}(0, 1)$')
            ax['hist_pan'].set_xlabel('Norm. Residuals')
            ax['hist_pan'].set_ylabel('Frequency Density')
            ax['hist_pan'].set_title(
                f'KS test: p-value = {self.goodness(statistic="ks"):.3f}')
            ax['hist_pan'].legend()
            if grid:
                ax['data_pan'].grid()
                ax['resi_pan'].grid()
                ax['hist_pan'].grid()
        return fig, ax

    def curve(self, x, return_hull=False, n_sigma=1):
        """
        Compute the fit curve and uncertainty hull.

        Parameters:
            x (ndarray): X values for the curve.
            return_hull (bool): Whether to return the uncertainty hull.
            n_sigma (float): Number of standard deviations for the hull.

        Returns:
            ndarray: Fit curve and uncertainty hull.
        """
        y = self._fitter.func(x, *self.popt)
        if return_hull:
            alldr = np.array([self._fitter.func(x, *self._allpr[i])
                              for i in range(self._allpr.shape[0])])
            q_h, q_l = gauss_quantiles(n_sigma=n_sigma)
            hull_l = np.quantile(alldr, q_l, axis=0)
            hull_h = np.quantile(alldr, q_h, axis=0)
            return np.array([y, hull_l, hull_h])
        else:
            return y

    def goodness(self, statistic='ks', method='mc', dof=None):
        """
        Compute the goodness-of-fit statistic.

        Parameters:
            statistic (str): Statistic to compute ('chi2' or 'ks').
            method (str): Method for computing the statistic ('mc' for Monte Carlo).
            dof (int): Degrees of freedom for chi-squared.

        Returns:
            float: P-value of the goodness-of-fit test.
        """
        if statistic.lower() == 'chi2':
            if dof is None:
                dof = len(self._data.x) - len(self.popt)
            pval = spe.gammaincc(dof/2, self.chi2/2)
        elif statistic.lower() == 'ks':
            if method is None:
                pval = stats.ks_1samp(self.residus_norm, stats.norm).pvalue
            elif method.lower() == 'mc':
                pval = stats.goodness_of_fit(stats.norm, self.residus_norm,
                                             known_params={
                                                 'loc': 0, 'scale': 1},
                                             statistic=statistic).pvalue
        return pval


class Data(object):

    def __init__(self, x, y, dx=None, dy=None):
        """
    Class to store data for fitting.

    Attributes:
        x (ndarray): X values.
        y (ndarray): Y values.
        dx (ndarray): Uncertainties in x.
        dy (ndarray): Uncertainties in y.
    """
        self.x = np.array(x)
        self.y = np.array(y)
        if len(self.x) != len(self.y):
            raise ValueError("x and y must have the same length")
        iter_dx = '__iter__' in dir(dx)
        iter_dy = '__iter__' in dir(dy)
        if iter_dx:
            self.dx = np.array(dx)
        else:
            if dx is None or dx == 0:
                self.dx = None
            else:
                self.dx = dx * np.ones_like(x)
        if iter_dy:
            self.dy = np.array(dy)
        else:
            if dy is None or dy == 0:
                self.dy = np.ones_like(y)
            else:
                self.dy = dy * np.ones_like(y)


def linfitxy(x, y, dx=None, dy=None, nb_loop=500, intercept=True, plot=False,
             draw_hull=True, marker='.', markercolor='tab:blue',
             linecolor='tab:orange', h_color=None, n_hull=100, h_min=None,
             h_max=None, fill_between=True,
             title=lin_title, labels=['x', 'y'], grid=True, statistic='ks_mc', dof=None,
             full_output=False, n_sigma=1):
    """
    Perform linear fitting with optional error propagation and visualization. 
    It assumes that uncertainties are independant and normally distributed.

    Parameters:
        x (array_like): X values.
        y (array_like): Y values.
        dx (array_like or scalar, optional): Uncertainties in x.
        dy (array_like or scalar, optional): Uncertainties in y.
        nb_loop (int, optional): Number of Monte Carlo iterations.
        intercept (bool, optional): Whether to include an intercept in the fit.
        plot (bool or str, optional): Whether to plot the fit results.
                                      Available options are: "simple" (same as True)
                                      for a plot including the data points with errorars, 
                                      the fitted curve and the hull if draw_hull is True, 
                                      "residuals" add a second ax with the residuals with 
                                      the errorbars, "resnorm" add a thirs ax containing 
                                      the histogram of the normalized residuals and the 
                                      gaussian $\mathcal{N}(\mu=0, \sigma=1)$ curve. 
        draw_hull (bool, optional): Whether to draw the uncertainty hull.
        marker (str, optional): Marker style for data points.
        markercolor (str, optional): Color of data points.
        linecolor (str, optional): Color of the fit line.
        h_color (str, optional): Color of the uncertainty hull.
        n_hull (int, optional): Number of points for the fit curve.
        h_min (float, optional): Minimum x value for the fit curve.
        h_max (float, optional): Maximum x value for the fit curve.
        fill_between (bool, optional): Whether to fill the uncertainty hull.
        title (str or callable, optional): Plot title.
        labels (list, optional): Axis labels.
        grid (bool, optional): Whether to display a grid.
        statistic (str, optional): Goodness-of-fit statistic ('ks_mc', 'ks', or 'chi2').
        dof (int, optional): Degrees of freedom for chi-squared.
        full_output (bool, optional): Whether to return full fit results.
        n_sigma (float, optional): Number of standard deviations for the uncertainty hull.

    Returns:
        ndarray: Fit results or fit parameters and uncertainties if full_output is False.
        dict: Fit results or fit parameters if full_output is True. 
              The list containing the fig and axes of the plot is included in the 
              dict only if plot is not None nor False
    """
    data = Data(x, y, dx, dy)
    func = LinFitXY.func_affine if intercept else LinFitXY.func_linear
    fitr = CurveFitY(func) if data.dx is None else LinFitXY(func)
    fres = fitr.fit(data, nb_loop=nb_loop)
    ind_sort = np.argsort(x)
    diffs = np.diff(x[ind_sort])
    dxline = np.min([diffs[0], diffs[-1]])
    if h_min is None:
        xmin = np.min(x)-dxline
    else:
        xmin = h_min
    if h_max is None:
        xmax = np.max(x)+dxline
    else:
        xmax = h_max
    xplot = np.linspace(xmin, xmax, n_hull)
    if statistic.lower() == 'ks_mc':
        statistic_, method_, dof_ = 'ks',  'mc',  None
    elif statistic.lower() == 'ks':
        statistic_, method_, dof_ = 'ks', None, None
    elif statistic.lower() == 'chi2':
        statistic_, method_, dof_ = 'chi2', None, dof
    if full_output:
        result = {'popt': fres.popt,
                  'perr': fres.sig,
                  'cov': fres.pcov,
                  'chi2': fres.chi2,
                  'residuals': fres.residus,
                  'norm_residuals': fres.residus_norm,
                  'goodness': fres.goodness(statistic=statistic_,
                                            method=method_, dof=dof_),
                  'curves': np.vstack([xplot, fres.curve(xplot,
                                                         return_hull=True,
                                                         n_sigma=n_sigma)])}
        if plot is not None and plot != False:
            result['fig_axes'] = fres.plot(xplot, style=plot,
                                           draw_hull=draw_hull,
                                           marker=marker,
                                           markercolor=markercolor,
                                           linecolor=linecolor,
                                           h_color=h_color,
                                           fill_between=fill_between,
                                           title=title,
                                           grid=grid,
                                           labels=labels)
        return result
    else:
        if plot is not None and plot != False:
            fres.plot(xplot, style=plot,
                      draw_hull=draw_hull,
                      marker=marker,
                      markercolor=markercolor,
                      linecolor=linecolor,
                      h_color=h_color,
                      fill_between=fill_between,
                      title=title,
                      grid=grid,
                      labels=labels)
        return fres.params


def curvefity(func, x, y, dy=None, p0=None, nb_loop=500, plot=False,
              draw_hull=True, marker='.', markercolor='tab:blue',
              linecolor='tab:orange', n_hull=100, h_color=None, h_min=None,
              h_max=None, fill_between=True, title=None, labels=None,
              grid=True, statistic='ks_mc', dof=None, full_output=False,
              n_sigma=1):
    """
    Perform curve fitting with optional error propagation and visualization.
    It assumes that uncertainties are independant and normally distributed.

    Parameters:
        func (callable): Function to fit.
        x (array_like): X values.
        y (array_like): Y values.
        dy (array_like or scalar, optional): Uncertainties in y.
        p0 (array_like): Initial guess for fit parameters.
        nb_loop (int, optional): Number of Monte Carlo iterations.
        plot (bool or str, optional): Whether to plot the fit results.
                                      Available options are: "simple" (same as True)
                                      for a plot including the data points with errorars, 
                                      the fitted curve and the hull if draw_hull is True, 
                                      "residuals" add a second ax with the residuals with 
                                      the errorbars, "resnorm" add a thirs ax containing 
                                      the histogram of the normalized residuals and the 
                                      gaussian $\mathcal{N}(\mu=0, \sigma=1)$ curve. 
        draw_hull (bool, optional): Whether to draw the uncertainty hull.
        marker (str, optional): Marker style for data points.
        markercolor (str, optional): Color of data points.
        linecolor (str, optional): Color of the fit line.
        h_color (str, optional): Color of the uncertainty hull.
        n_hull (int, optional): Number of points for the fit curve.
        h_min (float, optional): Minimum x value for the fit curve.
        h_max (float, optional): Maximum x value for the fit curve.
        fill_between (bool, optional): Whether to fill the uncertainty hull.
        title (str or callable, optional): Plot title.
        labels (list, optional): Axis labels.
        grid (bool, optional): Whether to display a grid.
        statistic (str, optional): Goodness-of-fit statistic ('ks_mc', 'ks', or 'chi2').
        dof (int, optional): Degrees of freedom for chi-squared.
        full_output (bool, optional): Whether to return full fit results.
        n_sigma (float, optional): Number of standard deviations for the uncertainty hull.

    Returns:
        ndarray: Fit results or fit parameters and uncertainties if full_output is False.
        dict: Fit results or fit parameters if full_output is True. 
              The list containing the fig and axes of the plot is included in the 
              dict only if plot is not None nor False
    """
    data = Data(x, y, None, dy)
    fitr = CurveFitY(func)
    fres = fitr.fit(data, p0=p0, nb_loop=nb_loop)
    if h_min is None:
        h_min = x.min()
    if h_max is None:
        h_max = x.max()
    xplot = np.linspace(h_min, h_max, n_hull)
    if statistic.lower() == 'ks_mc':
        statistic_, method_, dof_ = 'ks',  'mc',  None
    elif statistic.lower() == 'ks':
        statistic_, method_, dof_ = 'ks', None, None
    elif statistic.lower() == 'chi2':
        statistic_, method_, dof_ = 'chi2', None, dof
    if full_output:
        result = {'popt': fres.popt,
                  'perr': fres.sig,
                  'cov': fres.pcov,
                  'chi2': fres.chi2,
                  'residuals': fres.residus,
                  'norm_residuals': fres.residus_norm,
                  'goodness': fres.goodness(statistic=statistic_,
                                            method=method_, dof=dof_),
                  'curves': np.vstack([xplot, fres.curve(xplot,
                                                         return_hull=True,
                                                         n_sigma=n_sigma)])}
        if plot is not None and plot != False:
            result['fig_axes'] = fres.plot(xplot, style=plot,
                                           draw_hull=draw_hull,
                                           marker=marker,
                                           markercolor=markercolor,
                                           linecolor=linecolor,
                                           h_color=h_color,
                                           fill_between=fill_between,
                                           title=title,
                                           grid=grid,
                                           labels=labels)
        return result
    else:
        if plot is not None and plot != False:
            fres.plot(xplot, style=plot,
                      draw_hull=draw_hull,
                      marker=marker,
                      markercolor=markercolor,
                      linecolor=linecolor,
                      h_color=h_color,
                      fill_between=fill_between,
                      title=title,
                      grid=grid,
                      labels=labels)
        return fres.params
