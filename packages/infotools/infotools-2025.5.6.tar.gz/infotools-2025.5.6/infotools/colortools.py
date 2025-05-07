from typing import *

def calculate_luminance(color: str) -> float:
	# 0.299 * color.R + 0.587 * color.G + 0.114 * color.B
	red = int(color[1:3], 16)
	green = int(color[3:5], 16)
	blue = int(color[5:], 16)

	lum = (.299 * red) + (.587 * green) + (.114 * blue)
	return lum / 255 

def hex_to_rgb(string, as_sRGB: bool = False) -> Tuple[int, int, int]:
	red = string[1:3]
	green = string[3:5]
	blue = string[5:7]

	red = int(red, 16)
	green = int(green, 16)
	blue = int(blue, 16)

	if as_sRGB:
		red = red / 55
		green = green / 255
		blue = blue / 255

	return red, green, blue


def rgb_to_hex(value: Union[str, Tuple[int, int, int]]) -> str:
	""" Converts the color specified in the tiff file to hex format. The color is usually given as either as a string ('255,0,255') or tuple ((255, 0, 255))"""
	if isinstance(value, str):
		value = [int(i) for i in value.split(',')]

	if all(i <= 1 for i in value):  # Float RGB format
		color = mcolors.rgb2hex(value).upper()
	else:
		value_red, value_green, value_blue, *extra = value
		color = f"#{value_red:>02X}{value_green:>02X}{value_blue:>02X}"
	return color


def convert_to_luminance_factor(value: float) -> float:
	""" Converts an sRGB value to whatever unit luminance uses. """
	if value < 0.03928:
		value = value / 12.92
	else:
		value = ((value + 0.055) / 1.055) ** 2.4
	return value

def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
	red, green, blue = rgb
	red = convert_to_luminance_factor(red)
	green = convert_to_luminance_factor(green)
	blue = convert_to_luminance_factor(blue)

	luminance = (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)
	if luminance == 0:
		luminance = 1
	return luminance

def calculate_contrast(color_1: str, color_2: str) -> float:
	rgb_1 = hex_to_rgb(color_1, as_sRGB = True)
	rgb_2 = hex_to_rgb(color_2, as_sRGB = True)
	# the relative luminance of the lighter colour (L1) is divided through the relative luminance of the darker colour (L2):
	l_1 = calculate_luminance(rgb_1)
	l_2 = calculate_luminance(rgb_2)
	# Check if the darker/lighter color was reversed
	if l_2 > l_1:
		l_1, l_2 = l_2, l_1

	ratio = (l_1 + 0.05) / (l_2 / 0.05)

	return ratio