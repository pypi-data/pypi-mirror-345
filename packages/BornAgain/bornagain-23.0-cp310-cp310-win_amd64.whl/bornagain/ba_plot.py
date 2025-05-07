#  **************************************************************************  #
"""
#   BornAgain: simulate and fit reflection and scattering
#
#   @file      Wrap/Python/ba_plot.py
#   @brief     Python extensions of the SWIG-generated Python module bornagain.
#
#   @homepage  http://apps.jcns.fz-juelich.de/BornAgain
#   @license   GNU General Public License v3 or higher (see COPYING)
#   @copyright Forschungszentrum Juelich GmbH 2016
#   @authors   Scientific Computing Group at MLZ (see CITATION, AUTHORS)
"""
#  **************************************************************************  #

import math, os, pathlib, sys

import bornagain as ba
from bornagain.numpyutil import Arrayf64Converter as dac

try:
    import numpy as np
    import matplotlib as mpl
    from matplotlib import rc, pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except Exception as e:
    print(f"Import failure in ba_plot.py: {e}")

plotargs_default = {'figfile': None, 'label_fontsize': 16, 'legendloc': 'upper right'}
plotargs_default['cmap'] = os.environ.setdefault('CMAP', "inferno")


def env_to_bool(varname):
    if varname not in os.environ:
        return False
    value = os.environ[varname].lower()
    if value in ('false', 'off', 'n', 'no', '0'):
        return False
    if value in ('true', 'on', 'y', 'yes', '1'):
        return True
    raise Exception(
        f"Environment variable {varname} has ambiguous value {value}.")

if env_to_bool('USETEX'):
    rc('text', usetex=True)


#  **************************************************************************  #
#  internal functions
#  **************************************************************************  #

def parse_commandline():
    """ parse the arguments given on the command-line """

    plotargs1 = dict()

    # values from environment variables

    plotargs = dict(plotargs_default)

    for arg in sys.argv[1:]:
        s = arg.split("=")
        if len(s) != 2:
            raise Exception(f"command-line argument '{arg}' does not have form key=value")
        try:
            plotargs[s[0]] = int(s[1])
        except:
            plotargs[s[0]] = s[1]

    _figfile = plotargs.setdefault('figfile', plotargs_default['figfile'])

    return plotargs


def get_axes_limits(result):
    """
    Returns axes range as expected by pyplot.imshow.
    :param result: Datafield object from a Simulation
    :return: axes ranges as a flat list
    """
    limits = []
    for i in range(result.rank()):
        ax = result.axis(i)
        if ax.size() == 1:
            raise Exception(f'Axis {i} "{ax.axisLabel()}" has size 1:'
                            + ' rather plot <datafield>.flat()')
        ami = ax.min()
        ama = ax.max()
        assert ami < ama, f'Datafield has invalid axis {i}, extending from {ami} to {ama}'
        limits.append(ami)
        limits.append(ama)

    return limits


def translate_axis_label(label):
    """
    Formats an axis label into a LaTeX representation
    :param label: text representation of the axis label
    :return: LaTeX representation
    """
    label_dict = {
        'X (nbins)': r'$X \; $(bins)',
        'X (mm)': r'$X \; $(mm)',
        'Y (nbins)': r'$Y \; $(bins)',
        'Y (mm)': r'$Y \; $(mm)',
        'phi_f (rad)': r'$\varphi_f \; $(rad)',
        'phi_f (deg)': r'$\varphi_f \;(^\circ)$',
        'alpha_i (rad)': r'$\alpha_{\rm i} \; $(rad)',
        'alpha_i (deg)': r'$\alpha_{\rm i} \;(^\circ)$',
        'alpha_f (rad)': r'$\alpha_{\rm f} \; $(rad)',
        'alpha_f (deg)': r'$\alpha_{\rm f} \;(^\circ)$',
        'qx (1/nm)': r'$q_x \; $(nm$^{-1}$)',
        'qy (1/nm)': r'$q_y \; $(nm$^{-1}$)',
        'qz (1/nm)': r'$q_z \; $(nm$^{-1}$)',
        'q (1/nm)': r'$q \; $(nm$^{-1}$)',
        'lambda (nm)': r'$\lambda \; $(nm)',
        'Position (nm)': r'Position (nm)'
    }
    if label in label_dict.keys():
        return label_dict[label]
    return label


def get_axes_labels(result):
    """
    Returns axes range as expected by pyplot.imshow.
    :param result: Datafield object from a Simulation
    :return: axes ranges as a flat list
    Used internally and in Examples/fit/specular/RealLifeReflectometryFitting.py.
    """
    labels = []
    for i in range(result.rank()):
        labels.append(translate_axis_label(result.axis(i).axisLabel()))

    return labels


def plot_curve(xarray, yarray, **kwargs):
    """
    Used internally.
    """
    title = kwargs.pop('title', None)
    xlabel = kwargs.pop('xlabel', None)
    ylabel = kwargs.pop('ylabel', None)
    fontsize = kwargs.pop('label_fontsize', plotargs_default['label_fontsize'])

    if xlabel:
        plt.xlabel(xlabel, fontsize=fontsize)
    if ylabel:
        plt.ylabel(ylabel, fontsize=fontsize)
    if title:
        plt.title(title)

    inside_ticks()

    plt.plot(xarray, yarray)


def plot_specular_curve(result, **plotargs):
    """
    Plots intensity data for specular simulation result
    :param result: Datafield from SpecularSimulation
    Used internally.
    """
    pfield = result.plottableField()
    intensity = dac.asNpArray(pfield.dataArray())
    x_axis = pfield.axis(0).binCenters()

    xlabel = plotargs.pop('xlabel', get_axes_labels(pfield)[0])
    ylabel = plotargs.pop('ylabel', "Intensity")

    plt.yscale('log')

    ymax = plotargs.pop('intensity_max', np.amax(np.amax(intensity)*2))
    ymin = plotargs.pop('intensity_min',
                        max(np.amin(intensity)*0.5, 1e-18*ymax))
    plt.ylim([ymin, ymax])

    plot_curve(x_axis, intensity, xlabel=xlabel, ylabel=ylabel)


#  **************************************************************************  #
#  multiple frames in one plot
#  **************************************************************************  #

class MultiPlot:
    """
    Used internally.
    """

    def __init__(self, n, ncol, fontsize=None):
        self.n = n
        self.ncol = ncol
        self.nrow = 1 + (self.n - 1) // self.ncol

        # Parameters as fraction of subfig size.
        yskip = 0.2
        bottomskip = yskip
        topskip = yskip/2
        xskip = 0.18
        leftskip = xskip
        rightskip = 0.28 + ncol*0.03
        xtot = self.ncol*1.0 + (self.ncol - 1)*xskip + leftskip + rightskip
        ytot = self.nrow*1.0 + (self.nrow - 1)*yskip + bottomskip + topskip

        # We need parameters as fraction of total fig size.
        self.xskip = xskip/xtot
        self.leftskip = leftskip/xtot
        self.rightskip = rightskip/xtot
        self.yskip = yskip/ytot
        self.bottomskip = bottomskip/ytot
        self.topskip = topskip/ytot

        # Set total figure dimensions.
        ftot = 5
        if fontsize:
            self.fontsize = fontsize
        else:
            self.fontsize = 18 + 36.0/(ncol + 2)
        # Create the figure 'fig' and its subplots axes ('tmp'->'axes').
        self.fig, tmp = plt.subplots(self.nrow,
                                     self.ncol,
                                     figsize=(ftot*xtot, ftot*ytot))
        if n > 1:
            self.axes = tmp.flat
        else:
            self.axes = [tmp]

        # Adjust whitespace around and between subfigures.
        plt.subplots_adjust(wspace=self.xskip,
                            hspace=self.yskip,
                            left=self.leftskip,
                            right=1 - self.rightskip,
                            bottom=self.bottomskip,
                            top=1 - self.topskip)

    def plot_colorlegend(self, im):
        # Plot the color legend.
        cbar_ax = self.fig.add_axes([
            1 - self.rightskip + 0.4*self.xskip, self.bottomskip,
            0.25*self.xskip, 1 - self.bottomskip - self.topskip
        ])
        cb = self.fig.colorbar(im, cax=cbar_ax)
        cb.set_label(r'$\left|F(q)\right|^2/V^{\,2}$',
                     fontsize=self.fontsize)


#  **************************************************************************  #
#  versatile plot calls
#  **************************************************************************  #

def inside_ticks():
    """
    Ticks settings for xy plots: on all axes and pointing inside.
    Used internally and in a few examples.
    """
    plt.gca().yaxis.set_ticks_position('both')
    plt.gca().xaxis.set_ticks_position('both')
    plt.gca().tick_params(which='both', direction='in')


def plot_simres(result, **kwargs):
    """
    Plots intensity data as heat map
    :param result: Datafield from GISAS/OffspecSimulation
    Used internally and in a few examples.
    """

    pfield = result.plottableField()
    axes_limits = get_axes_limits(pfield)
    axes_labels = get_axes_labels(pfield)

    if 'xlabel' not in kwargs:
        kwargs['xlabel'] = axes_labels[0]
    if 'ylabel' not in kwargs:
        kwargs['ylabel'] = axes_labels[1]

    array = dac.asNpArray(result.dataArray())
    assert len(array.shape) == 2
    assert array.shape[0] > 0
    assert array.shape[1] > 0
    if axes_limits is not None:
        assert len(axes_limits) == 4
        assert axes_limits[0] < axes_limits[
            1], f'Invalid x interval {axes_limits[0]} .. {axes_limits[1]}'
        assert axes_limits[2] < axes_limits[
            3], f'Invalid y interval {axes_limits[2]} .. {axes_limits[3]}'

    zmax = kwargs.pop('intensity_max', np.amax(array))
    zmin = kwargs.pop('intensity_min', 1e-6*zmax)

    if zmin == zmax == 0.0:
        norm = mpl.colors.Normalize(0, 1)
    else:
        norm = mpl.colors.LogNorm(zmin, zmax)

    xlabel = kwargs.pop('xlabel', None)
    ylabel = kwargs.pop('ylabel', None)
    zlabel = kwargs.pop('zlabel', "Intensity")
    title = kwargs.pop('title', None)
    aspect = kwargs.pop('aspect', 'equal')
    cmap = kwargs.pop('cmap', plotargs_default['cmap'])
    withCBar = kwargs.pop('with_cb', True)

    ax = plt.gca()
    im = ax.imshow(array,
                   origin='lower',
                   cmap=cmap,
                   norm=norm,
                   aspect=aspect,
                   extent=axes_limits)

    if xlabel:
        plt.xlabel(xlabel, fontsize=plotargs_default['label_fontsize'])
    if ylabel:
        plt.ylabel(ylabel, fontsize=plotargs_default['label_fontsize'])
    if title:
        plt.title(title)

    if withCBar:
        aspect = 20

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="7%", pad="5%")
        cb = plt.colorbar(im, cax=cax)
        if zlabel:
            cb.set_label(zlabel, size=plotargs_default['label_fontsize'])

    return im

#  **************************************************************************  #
#  deprecated user calls
#  **************************************************************************  #

def plot_histogram(field, **kwargs):
    raise Exception("Since BornAgain 22, function plot_histogram has been replaced " +
                    "by function plot_datafield")

def make_plot(field, **kwargs):
    raise Exception("Since BornAgain 22, function make_plot has been replaced " +
                    "by function plot_to_grid")

def make_plot_row(field, **kwargs):
    raise Exception("Since BornAgain 22, function make_plot_row has been replaced " +
                    "by function plot_to_row")


#  **************************************************************************  #
#  standard user calls
#  **************************************************************************  #

def export(**plotargs):
    _figfile = plotargs.pop('figfile', None)
    if _figfile:
        plt.savefig(_figfile, bbox_inches='tight')


def plot_datafield(result, **plotargs):
    """
    Draws simulation result and (optionally) shows the plot.
    """

    if len(dac.asNpArray(result.dataArray()).shape) == 1:
        # 1D data => assume specular simulation
        plot_specular_curve(result, **plotargs)
    else:
        plot_simres(result, **plotargs)


def plot_to_row(results, **plotargs):
    plot_to_grid(results, len(results), **plotargs)


def plot_to_grid(results, ncol, **plotargs):
    """
    Make a plot consisting of one detector image for each Result in results,
    plus one common color legend.

    :param results: List of simulation results
    :param ncol:    Maximum number of plot frames per row
    """
    pfields = [result.plottableField() for result in results]
    multiPlot = MultiPlot(len(pfields), ncol,
                          plotargs.pop('fontsize', None))
    cmap = plotargs.pop('cmap', plotargs_default['cmap'])

    # Always the same color legend, to facilitate comparisons between figures.
    norm = mpl.colors.LogNorm(1e-8, 1)
    # Plot the subfigures.
    for i, pfield in enumerate(pfields):
        ax = multiPlot.axes[i]
        axes_limits = get_axes_limits(pfield)

        im = ax.imshow(dac.asNpArray(pfield.dataArray()),
                       origin='lower',
                       cmap=cmap,
                       norm=norm,
                       extent=axes_limits,
                       aspect=1)

        ax.set_xlabel(r'$\varphi_{\rm f} (^{\circ})$',
                      fontsize=multiPlot.fontsize)
        if i % ncol == 0:
            ax.set_ylabel(r'$\alpha_{\rm f} (^{\circ})$',
                          fontsize=multiPlot.fontsize)
        if pfield.title() != "":
            ax.set_title(pfield.title(), fontsize=multiPlot.fontsize)
        ax.tick_params(axis='both',
                       which='major',
                       labelsize=multiPlot.fontsize*21/24)

    multiPlot.plot_colorlegend(im)


def plot_multicurve_specular(results):
    raise Exception("Function bp.plot_multicurve_specular has become "
                    "bp.plot_multicurve in BornAgain 22")


def plot_multicurve(results, **plotargs):
    plt.yscale('log')
    pfields = [result.plottableField() for result in results]

    legend = []
    for pfield in pfields:
        x = pfield.axis(0).binCenters()
        y = dac.asNpArray(pfield.dataArray())
        legend.append(pfield.title())
        plt.plot(x, y)

    inside_ticks()

    plt.xlabel(get_axes_labels(pfields[0])[0])
    plt.ylabel(r'Intensity')

    plt.legend(legend, loc=plotargs.pop('legendloc', 'upper right'))
