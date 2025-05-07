import math
from dataclasses import dataclass, field
from typing import *
from loguru import logger
from fuzzywuzzy import process

NumberType = Union[int, float]


@dataclass
class Magnitude:
	""" Provides an easy method of checking the magnitude of numbers."""
	prefix: str
	suffix: str
	multiplier: NumberType
	alias: List[str] = field(default_factory = list)  # Alternative methods of referring to this multiplier.

	def __str__(self)->str:
		label = f"Magnitude({self.prefix=}, {self.suffix=}, {self.multiplier=:E}, {self.alias=})"
		return label
	@staticmethod
	def _get_other(other):
		""" Returns the value in `other` that the dunder methods need to compare.
		"""
		if hasattr(other, 'multiplier'):
			return other.multiplier
		else:
			return other

	def __float__(self) -> float:
		return float(self.multiplier)

	def __post_init__(self):
		self.alias.append(self.prefix)

	def __mul__(self, other) -> float:
		return self._get_other(other) * self.multiplier

	def __rmul__(self, other) -> float:
		return self.__mul__(other)

	def __ge__(self, other):
		other = self._get_other(other)
		return self.multiplier >= other

	def __gt__(self, other) -> bool:
		other = self._get_other(other)
		return self.multiplier > other

	def __lt__(self, other):
		other = self._get_other(other)
		return self.multiplier < other

	def __le__(self, other):
		other = self._get_other(other)
		return self.multiplier <= other

	def __eq__(self, other):
		other = self._get_other(other)
		return self.multiplier == other

	def is_match(self, value: str) -> bool:
		""" Returns True if the passed string corresponds to this scale."""
		selected_scale = False
		if self.prefix == value or self.suffix == value:
			selected_scale = True
		else:
			scale_alias, score = process.extractOne(value.lower(), self.alias)
			if score > 90:
				selected_scale = True
		return selected_scale


class AbstractScale:
	def __init__(self):
		self.system: List[Magnitude] = []

	@staticmethod
	def is_null(value) -> bool:
		""" Checks if a value represents a null value."""
		try:
			result = value is None or math.isnan(float(value))
		except (TypeError, ValueError):
			result = True

		return result

	def get_unit_magnitude(self):
		raise NotImplementedError

	def get_magnitude_from_value(self, value: SupportsAbs) -> Magnitude:
		value = abs(value)

		if value == 0.0 or self.is_null(value):
			return self.get_unit_magnitude()

		for _scale in self.system[::-1]:

			if value >= _scale.multiplier:
				magnitude = _scale
				break
		else:
			message = f"'{value}' does not have a defined base."
			raise ValueError(message)

		return magnitude

	def get_magnitude_from_prefix(self, prefix: str) -> Optional[Magnitude]:
		"""
			Retrieves the `Magnitude` object where `Magnitude.prefix` or `Magnitude.suffix` equals `prefix`
		"""
		try:
			candidates = [i for i in self.system if (i.prefix == prefix or i.suffix == prefix)]
			return candidates[0]
		except IndexError:
			return None

	def get_magnitude_from_alias(self, alias: str) -> Optional[Magnitude]:
		for element in self.system:
			if not element.alias:
				# Don't bother with empty aliases.
				continue
			candidate, score = process.extractOne(alias.lower(), element.alias)
			if score > 90:
				return element
		# Added to make it clear the method should return `None`
		return None

	def get_magnitude(self, value:Union[NumberType, str])->Optional[Magnitude]:
		"""
			Returns a `Magnitude` object where one attribute matches `value`.
		"""
		if isinstance(value, str):
			magnitude = self.get_magnitude_from_prefix(value)
			if magnitude is None:
				magnitude = self.get_magnitude_from_alias(value)
		elif isinstance(value, Magnitude):
			magnitude = value
		else:
			magnitude = self.get_magnitude_from_value(value)
		return magnitude

	def get_multiplier(self, source:Union[str, NumberType,Magnitude], target:str)->NumberType:
		"""
			Returns the multipler to convert from the scale `source` to `target`.
			Parameters
			----------
			source, target: Union[str, NumberType,Magnitude]
				Identifies the `Magnitude` to use.
		"""
		source_magnitude = self.get_magnitude(source)
		target_magnitude = self.get_magnitude(target)

		multiplier = source_magnitude.multiplier / target_magnitude.multiplier
		return multiplier


	def convert_scale(self, value:NumberType,  target:str, base:str = None):
		"""
			Converts a number to a target scale.
			Parameters
			----------
			value: NumberType
				The value to convert.
			target: str
				The prefix or alias of the magnitude to convert to. Ex. 'T', 'femto'

			Returns
			-------
			NumberType
		"""
	def convert(self, value: NumberType, target: str, base:Optional[str] = 'unit') -> NumberType:
		"""
			Converts a number to a target scale.
			Parameters
			----------
			value: NumberType
				The value to convert.
			target: str
				The prefix or alias of the magnitude to convert to. Ex. 'T', 'femto'
			base: Optional[str] = 'unit'
				The current base of `value`. Defaults to `unit` so by default the function simply converts the number as given
				into the target base. If given, the method will convert `value` from the source base to the target base.
			Returns
			-------
			NumberType
		"""
		multiplier = self.get_multiplier(base, target)
		return value * multiplier


class DecimalScale(AbstractScale):
	def __init__(self):
		super().__init__()
		self.base = 10
		self.system = [
			Magnitude('atto', 'a', 1E-18),
			Magnitude('femto', 'f', 1E-15),
			Magnitude('pico', 'p', 1E-12),
			Magnitude('nano', 'n', 1E-9),
			Magnitude('micro', "μ", 1E-6, ["u", 'millionths']),
			Magnitude('milli', 'm', 1E-3, ['thousandths']),
			Magnitude('', '', 1E0, ['unit', 'one']),
			Magnitude('kilo', 'K', 1E3, ['thousand']),
			Magnitude('mega', 'M', 1E6, ['million']),
			Magnitude('giga', 'B', 1E9, ['billion']),
			Magnitude('tera', 'T', 1E12, ['trillion']),
			Magnitude('peta', 'P', 1E15, ['quadrillion']),
			Magnitude('exa', 'E', 1E18, ['quintillion'])
		]


	def get_unit_magnitude(self) -> Magnitude:
		return self.system[6]


class BinaryScale(AbstractScale):
	def __init__(self):
		super().__init__()
		self.base = 1024
		self.system = [
			Magnitude('', '', self.base ** 0, ['unit', '']),
			Magnitude('kibi', 'KiB', self.base ** 1, ['thousand']),
			Magnitude('mebi', 'MiB', self.base ** 2, ['million']),
			Magnitude('gibi', 'GiB', self.base ** 3, ['billion']),
			Magnitude('tebi', 'TiB', self.base ** 4, ['trillion']),
			Magnitude('pebi', 'PiB', self.base ** 5, ['quadrillion']),
			Magnitude('exbi', 'EiB', self.base ** 6, ['quintillion']),
			Magnitude('zebi', 'ZiB', self.base ** 7, []),
			Magnitude('yobi', 'YiB', self.base ** 8, [])
		]

	def get_unit_magnitude(self):
		return self.system[0]


if __name__ == "__main__":
	scale = BinaryScale()
	value = 1_000_000_000
	print(scale.get_magnitude_from_value(value))
