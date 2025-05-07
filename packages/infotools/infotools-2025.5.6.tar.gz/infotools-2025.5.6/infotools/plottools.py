from typing import *

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from infotools import numbertools
import random

class Palette:
	def __init__(self, colormap: str = "Blues", step:int = 10):
		self.breakpoints = [i * step for i in range(10)]
		self.colors = seaborn.color_palette(colormap, len(self.breakpoints) + 1)

		self.colormap_bins = {cutoff: color for cutoff, color in zip(self.breakpoints, self.colors)}

	def get_color(self, value: float) -> str:
		for cutoff, color in self.colormap_bins.items():
			if value <= cutoff:
				break
		else:
			color = '#FF0000'
		return color

	def add_legend(self, ax: plt.Axes, colormap: Dict[str, str] = None, **kwargs) -> plt.Axes:
		if colormap is None:
			colormap = self.colormap_bins
		ax = add_legend(ax, colormap,**kwargs)
		return ax



def add_legend(ax: plt.Axes, colormap: Dict[str, str], keep_order:bool = False,  **kwargs) -> plt.Axes:

	items = colormap.items() if keep_order else sorted(colormap.items())

	patches = list()
	for label, color in items:
		patch = mpatches.Patch(color = color, label = label)
		patches.append(patch)

	ax.legend(handles = patches, **kwargs)
	return ax


def get_random_color(lower: int = 50, upper: int = 250) -> str:
	red = random.randint(lower, upper)
	green = random.randint(lower, upper)
	blue = random.randint(lower, upper)
	return f"#{red:>02X}{green:>02X}{blue:>02X}"


def hr_labels(ax: plt.Axes, which: Literal['x', 'y', 'xy', 'both'] = 'y') -> plt.Axes:
	""" Converts numerical values into a human-friendly format.
		Parameters
		----------
		ax:plt.Axes
			The ax object that needs to be modified.
		which: Literal['x', 'y', 'xy', 'both']; default 'y'
			Specifies which axis to modify.
		Returns
		-------
		plt.Axes
			The modified ax object.
	"""
	if which in {'x', 'xy', 'both'}:
		x_ticks = ax.xaxis.get_majorticklocs()
		x_labels = [numbertools.human_readable(i) for i in x_ticks]
		ax.set_xticklabels(x_labels)

	if which in {'y', 'xy', 'both'}:
		y_ticks = ax.yaxis.get_majorticklocs()
		y_labels = [numbertools.human_readable(i) for i in y_ticks]
		ax.set_yticklabels(y_labels)

	return ax
