"""
	Suite of tests for numbertools
"""

import pytest

from infotools import numbertools


@pytest.fixture
def decimal() -> numbertools.DecimalScale:
	return numbertools.DecimalScale()


def test_decimalscale_get_unit_magnitude(decimal):
	result = decimal.get_unit_magnitude()
	assert result.multiplier == 1


@pytest.mark.parametrize(
	"value, expected_multiplier",
	[
		(0.00013, 1E-6),
		(0.1010, 1E-3),
		(0, 1),
		(1, 1),
		(10, 1),
		(12_123_456, 1E6)
	]
)
def test_decimalscale_get_magnitude_from_value(decimal, value, expected_multiplier):
	result = decimal.get_magnitude_from_value(value)
	assert result.multiplier == expected_multiplier


@pytest.mark.parametrize(
	"prefix, expected_multiplier",
	[
		("μ", 1E-6),
		("micro", 1E-6),
		("m", 1E-3),
		("milli", 1E-3),
		('', 1),
		('M', 1E6),
		('mega', 1E6),
		('P', 1E15),
		('peta', 1E15)
	]
)
def test_decimalscale_get_magnitude_from_prefix(decimal, prefix, expected_multiplier):
	result = decimal.get_magnitude_from_prefix(prefix)
	assert result.multiplier == expected_multiplier


@pytest.mark.parametrize(
	"alias, expected_multiplier",
	[
		('unit', 1),
		("millionths", 1E-6),
		("trillion", 1E12),
	]
)
def test_decimalscale_get_magnitude_from_alias(decimal, alias, expected_multiplier):
	result = decimal.get_magnitude_from_alias(alias)
	assert result.multiplier == expected_multiplier
@pytest.mark.parametrize(
	"value, expected_multiplier",
	[
		('u', 1E-6),
		("μ", 1E-6),
		('millionths', 1E-6),
		(0.000123, 1E-6),
		("micro", 1E-6),
		("m", 1E-3),
		("milli", 1E-3),
		("thousandths", 1E-3),
		(0.123, 1E-3),
		('', 1),
		('K', 1E3),
		('kilo', 1E3),
		('thousand', 1E3),
		('Thousand', 1E3),
		(453999.999, 1E3),
		('M', 1E6),
		('mega', 1E6),
		(123_456_789, 1E6),
		('P', 1E15),
		('peta', 1E15)
	]
)
def test_decimalscale_get_magnitude(decimal, value, expected_multiplier):
	result = decimal.get_magnitude(value)
	assert result.multiplier == expected_multiplier

@pytest.mark.parametrize(
	"source, target, expected",
	[
		('unit', 'K', 1E-3),
		('unit', 'f', 1E15),
		('micro', 'K', 1E-9),
		('B', 'T', 1E-3),
		('T', 'unit', 1E12),
		('T', 'B', 1E3),
		(123_456_789_111_222, 'unit', 1E12)
	]
)
def test_get_multiplier(decimal, source, target, expected):
	result = decimal.get_multiplier(source, target)
	assert result == pytest.approx(expected)


@pytest.mark.parametrize(
	"value, target, expected",
	[
		(0, 'f', 0),
		(0, 'K', 0),
		(1, 'f', 1E15),
		(1, 'B', 1E-9),
		(123_456_789_111_222, 'unit', 123_456_789_111_222),
		(123_456_789_111_222, 'T', 123.456789111222),
		(123_456_789_111_222, 'B', 123456.789111222),
		(123_456_789_111_222, 'm', 123_456_789_111_222_000),
		(-500_000_000_000.0,'T', -0.500),
		(1234.123,"unit", 1234.123),
		(1234.123,"", 1234.123)
	]
)
def test_decimalscale_convert_value(decimal, value, target, expected):
	result = decimal.convert(value, target)
	assert pytest.approx(result) == expected


@pytest.fixture
def binary() -> numbertools.BinaryScale:
	return numbertools.BinaryScale()


@pytest.mark.parametrize("value,expected",
	[
		(123.456, True),
		('123.456', True),
		('abc', False),
		('12.345.678', False),
		("1E6", True),
		([123, "456.f", "789.0"], [True, False, True])
	])
def test_is_number(value, expected):
	assert expected == numbertools.is_number(value)


@pytest.mark.parametrize(
	"number,precision,base,expected",
	[
		(1234.123, 6, None, '1.234123K'),
		(12.5E-6, 1, None, '12.5μ'),
		(111_222_333_444_555, 12, None, '111.222333444555T'),
		(-1234.123, 6, None, '-1.234123K'),
		(-500_000_000_000.0, 2, None, "-500.00B"),
		(-500_100_000_000.0, 2, None, "-500.10B"),
		(-500_000_000_000.0, 0, None, "-500B"),
		(0.0, 0, None, "0"),
		(0.0, 2, None, "0.00"),
		(1234.123, 3, "unit", '1234.123'),
		(111_222_333_444_555, 2, 'B', '111222.33B'),
		(-500_000_000_000.0, 3, 'T', "-0.500T"),
		(-500_000_000_000.0, 2, 'T', "-0.50T")
	]
)
def test_human_readable_1(number, precision, base, expected):
	assert numbertools.human_readable(number, precision = precision, base = base) == expected

@pytest.mark.parametrize(
	"number, precision, base, system, expected",
	[
		(1_000_000, 2, None, 'decimal', '1.00M'),
		(1_000_000, 2, None, 'binary', '976.56KiB'),
		(1_000_000_000, 1, None, 'decimal', '1.0B'),
		(1_000_000_000, 1, None, 'binary', '953.7MiB')
	]
)
def test_human_readable_2(number, precision, base, system, expected):
	assert numbertools.human_readable(number, precision = precision, base = base, system = system) == expected
@pytest.mark.parametrize(
	"value,expected",
	[
		("5.4", 5.4),
		('asfkjnlmlqwe', None),
		('7.8/10 ', 0.78)
	]
)
def test_convert_string_to_number(value, expected):
	result = numbertools.to_number(value, default = None)

	assert result == expected


@pytest.mark.parametrize(
	"value,expected",
	[
		("5.4", 5.4),
		('asfkjnlmlqwe', None),
		('7.8/10 ', 0.78),
		(['7.8/10', '99'], [0.78, 99])
	]
)
def test_to_number(value, expected):
	result = numbertools.to_number(value, None)

	assert result == expected


@pytest.mark.parametrize(
	"value",
	[
		"kilo", "micro", "milli", "femto"
	]
)
def test_get_magnitude_from_prefix(value):
	result = numbertools.DecimalScale().get_magnitude_from_prefix(value)
	assert result.prefix == value


@pytest.mark.parametrize(
	"system", [numbertools.DecimalScale(), numbertools.BinaryScale()]
)
def test_get_unit_magnitude(system):
	assert system.get_unit_magnitude() == system.get_magnitude_from_alias('unit')


@pytest.mark.parametrize(
	"value,expected",
	[
		(1234, 'kilo'),
		(1E-4, 'micro'),
		(0.123, 'milli'),
		(0.0, "")
	]
)
def test_get_magnitude_from_value(decimal, value, expected):
	result = decimal.get_magnitude_from_value(value)
	assert result.prefix == expected


@pytest.mark.parametrize(
	"value,expected",
	[
		('billion', 'giga'),
		('Millions', 'mega')
	]
)
def test_get_magnitude_from_alias(decimal, value, expected):
	result = decimal.get_magnitude_from_alias(value)

	assert result.prefix == expected
