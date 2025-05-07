from pathlib import Path
import numpy
import pytest
from loguru import logger

from infotools import filetools
import datetime


@pytest.mark.parametrize(
	"filename, expected",
	[
		("file1.mp4", ('video', 'mp4')),
		("abc.aac", ("audio", "aac"))
	]
)
def test_get_mimetype(filename, expected):
	assert filetools.get_mimetype(filename) == expected


def test_checkdir(tmp_path):
	folder = Path(__file__).parent / "new"
	result = filetools.checkdir(folder)

	logger.debug(f"Folder: {folder}, {type(folder)}, {folder.exists()}")
	logger.debug(f"result: {result}, {type(result)}, {result.exists()}")
	logger.debug(f"{result == folder}")
	assert result == folder
	assert result.exists()


@pytest.mark.parametrize(
	"obj, expected",
	[
		(Path(__file__), __file__),  # Convert Path to str
		(numpy.linspace(0, 10, 21), [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]),
		(numpy.float64(10), 10.0),
		(numpy.float64(5.3), 5.3),
		(datetime.date(2022, 7, 13), "2022-07-13"),
		(datetime.datetime(2022, 9, 13, 4, 9, 39), "2022-09-13T04:09:39"),
		(datetime.timedelta(seconds = 123), f"0:02:03")
	]
)
def test_to_json(obj, expected):
	result = filetools.to_json(obj)
	assert result == expected
	assert type(result) == type(expected)
