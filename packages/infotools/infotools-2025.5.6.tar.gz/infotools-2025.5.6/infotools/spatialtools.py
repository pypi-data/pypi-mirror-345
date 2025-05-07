from typing import *
from pathlib import Path
import numpy

def calculate_area_of_polygon(x:numpy.ndarray, y:numpy.ndarray):
	return 0.5 * numpy.abs(numpy.dot(x, numpy.roll(y, 1)) - numpy.dot(y, numpy.roll(x, 1)))

def main():
	pass


if __name__ == '__main__':
	main()
