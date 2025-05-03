r"""A plot with $v_\text{wall}$ on the x-axis and $\alpha_n$ on the y-axis."""

import typing as tp

from matplotlib.colors import Colormap
from matplotlib.contour import QuadContourSet
from matplotlib.legend import Legend
import matplotlib.pyplot as plt
import numpy as np

from pttools.analysis.bubble_grid import BubbleGridVWAlpha
from pttools.analysis import colormap
from pttools.analysis.colormap import REGION_COLOR_DEFAULT
from pttools.bubble.chapman_jouguet import v_chapman_jouguet


class VwAlphaPlot:
    r"""A plot with $v_\text{wall}$ on the x-axis and $\alpha_n$ on the y-axis."""
    def __init__(
            self,
            grid: BubbleGridVWAlpha,
            fig: plt.Figure = None,
            ax: plt.Axes = None,
            title: str = None,
            alpha_label: str = r"$\alpha_n$"):
        self.grid = grid

        if fig is None:
            if ax is not None:
                raise ValueError("Cannot provide ax without fig")
            self.fig = plt.figure()
        else:
            self.fig = fig

        self.ax = self.fig.add_subplot() if ax is None else ax
        self.ax.set_xlabel(r"$v_\text{wall}$")
        self.ax.set_ylabel(alpha_label)
        self.ax.set_xlim(grid.v_walls.min(), grid.v_walls.max())
        self.ax.set_ylim(grid.alpha_ns.min(), grid.alpha_ns.max())
        # self.ax.set_xlim(0, 1)
        # self.ax.set_ylim(0, 1)
        self.ax.grid()
        if title is not None:
            self.ax.set_title(title)

    def contourf_plusminus(
            self,
            data: np.ndarray,
            label: str,
            diff_level: float = None,
            cmap_neg: tp.Union[Colormap, str] = colormap.CMAP_NEG_DEFAULT,
            cmap_pos: tp.Union[Colormap, str] = colormap.CMAP_POS_DEFAULT):
        """Add a contour plot to the figure"""
        if diff_level is None:
            diff_level = 0.1
        levels, colors = colormap.cmap_plusminus(
            min_level=np.nanmin(data), max_level=np.nanmax(data), diff_level=diff_level,
            cmap_neg=cmap_neg, cmap_pos=cmap_pos
        )
        cs: QuadContourSet = self.ax.contourf(
            self.grid.v_walls, self.grid.alpha_ns, data, levels=levels, colors=colors)
        cbar = self.fig.colorbar(cs)
        cbar.ax.set_ylabel(label)

    def color_region(self, region: np.ndarray, color: str = REGION_COLOR_DEFAULT, alpha: float = 1) -> QuadContourSet:
        """Color a region with a fixed color"""
        return colormap.color_region(
            ax=self.ax, x=self.grid.v_walls, y=self.grid.alpha_ns,
            region=region, color=color, alpha=alpha
        )

    def chapman_jouguet(self, color: str = "black", ls: str = "--", label: str = "$v_{CJ}$") -> tp.List[plt.Line2D]:
        """Add a Chapman-Jouguet speed curve to the plot"""
        return self.ax.plot(
            v_chapman_jouguet(self.grid.model, self.grid.alpha_ns),
            self.grid.alpha_ns, color=color, ls=ls, label=label
        )

    def legend(self, *args, **kwargs) -> Legend:
        """Add a legend to the plot"""
        return self.ax.legend(*args, **kwargs)
