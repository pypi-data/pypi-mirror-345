"""Utilties for plotting the spectrum of a single bubble"""

import matplotlib.pyplot as plt
import numpy as np

from pttools.analysis.utils import A4_PAPER_SIZE, FigAndAxes, create_fig_ax, legend
from pttools.ssmtools.spectrum import SSMSpectrum

SPEC_DEN_V_LABEL = r"$\mathcal{P}_{v}(kR_*)$"
SPEC_DEN_GW_LABEL = r"$\mathcal{P}_{gw}(kR_*)$"
POW_V_LABEL = r"$\mathcal{P}_{\tilde{v}}(kR_*)$"
POW_GW_LABEL = r"$\mathcal{P}_{\tilde{gw}}(kR_*)$"
OMGW0_LABEL = r"$\Omega_{gw,0}$"


def plot_spectrum(
        spectrum: SSMSpectrum,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        path: str = None,
        **kwargs) -> FigAndAxes:
    rf"""Plot the GW spectrum {POW_GW_LABEL} of a bubble"""
    fig, ax = create_fig_ax(fig, ax)
    ax.plot(spectrum.y, spectrum.pow_gw, **kwargs)
    ax.set_ylabel(POW_GW_LABEL)
    return plot_spectrum_common(spectrum, fig, ax, path)


def plot_spectrum_common(spectrum: SSMSpectrum, fig: plt.Figure, ax: plt.Axes, path: str = None) -> FigAndAxes:
    """Common steps for plotting a spectrum"""
    ax.set_xlabel("$z$")
    ax.set_xlim(np.min(spectrum.y), np.max(spectrum.y))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid()
    legend(ax)
    if path is not None:
        fig.savefig(path)
    return fig, ax


def plot_spectrum_multi(spectrum: SSMSpectrum, fig: plt.Figure = None, path: str = None, **kwargs) -> plt.Figure:
    """Plot multiple types of spectra for a bubble"""
    if fig is None:
        fig = plt.figure(figsize=A4_PAPER_SIZE)
    axs = fig.subplots(2, 2)
    plot_spectrum_spec_den_v(spectrum, fig, axs[0, 0], **kwargs)
    plot_spectrum_spec_den_gw(spectrum, fig, axs[1, 0], **kwargs)
    plot_spectrum_v(spectrum, fig, axs[0, 1], **kwargs)
    plot_spectrum(spectrum, fig, axs[1, 1], **kwargs)
    fig.tight_layout()
    if path is not None:
        fig.savefig(path)
    return fig


def plot_spectrum_v(
        spectrum: SSMSpectrum,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        path: str = None,
        **kwargs) -> FigAndAxes:
    rf"""Plot the velocity power spectrum {POW_V_LABEL} of a bubble"""
    fig, ax = create_fig_ax(fig, ax)
    ax.plot(spectrum.y, spectrum.pow_v, **kwargs)
    ax.set_ylabel(POW_V_LABEL)
    return plot_spectrum_common(spectrum, fig, ax, path)


def plot_spectrum_spec_den_gw(
        spectrum: SSMSpectrum,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        path: str = None,
        **kwargs) -> FigAndAxes:
    rf"""Plot the spectral density of GWs {SPEC_DEN_GW_LABEL} for a bubble"""
    fig, ax = create_fig_ax(fig, ax)
    ax.plot(spectrum.y, spectrum.spec_den_gw, **kwargs)
    ax.set_ylabel(SPEC_DEN_GW_LABEL)
    return plot_spectrum_common(spectrum, fig, ax, path)


def plot_spectrum_spec_den_v(
        spectrum: SSMSpectrum,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        path: str = None,
        **kwargs) -> FigAndAxes:
    rf"""Plot the spectral density of velocity {SPEC_DEN_V_LABEL} for a bubble"""
    fig, ax = create_fig_ax(fig, ax)
    ax.plot(spectrum.y, spectrum.spec_den_v, **kwargs)
    ax.set_ylabel(SPEC_DEN_V_LABEL)
    return plot_spectrum_common(spectrum, fig, ax, path)
