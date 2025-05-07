from pathlib import Path
from typing import Dict, Union

import pandas


def read_table(file_name: Union[str, Path], **kwargs):
	""" Reads the table and returns a dataframe. This is basically just a short script that lets
		users import data without having to worry about filetype.
	"""
	file_name = Path(file_name)
	extension = file_name.suffix
	default_args = {
		'.csv': {'delimiter': ','},
		'.tsv': {'delimiter': '\t'}
	}

	# arguments = self._cleanArguments(extension, arguments)
	file_name = str(file_name.absolute())
	if extension in {'.xls', '.xlsx', '.xlsm'}:  # .xlsm is not a typo.

		df = pandas.read_excel(file_name, **kwargs)
	elif extension in {'.csv', '.tsv', '.fsv', '.txt'}:
		arguments = {**default_args.get(extension), **kwargs}
		if 'sheetname' in arguments: arguments.pop('sheetname')
		df = pandas.read_table(file_name, **arguments)
	elif extension == '.pkl':
		df = pandas.read_pickle(file_name)
	else:
		raise NameError("{} does not have a valid extension!".format(file_name))
	return df


def to_spreadsheet(tables: Dict[str, pandas.DataFrame], filename: Path, include_index: bool = True) -> Path:
	"""
		Saves the table as an Excel spreadsheet, where multiple tables can be given..
	Parameters
	----------
	tables: Dict[str,pandas.DataFrame]
		A mapping of sheet names to dataframes.

	filename: str, pathlib.Path
		The output file.

	Returns
	-------
	Path: The output filename
	"""
	#writer = pandas.ExcelWriter(str(filename))
	# python 3.5 or 3.6 made all dicts ordered by default, so the sheets will be ordered in the same order they were defined in `tables`
	with pandas.ExcelWriter(str(filename)) as writer:
		for sheet_label, table in tables.items():
			if table is None:
				continue
			table.to_excel(writer, sheet_name = sheet_label, index = include_index)

	# Need to use the xlsx library to change some features of the spreadsheet.

	return filename

def to_csv(table:pandas.DataFrame, filename:Path, precision:int = 2):
	"""
		A wrapper around csv/pandas that removes insignificant digits from the values in numerical columns.
		Parameters
		----------
		filename:Path
			Filename to the output table
	"""

	for column_label in table.columns:
		column = table[column_label]
		is_numeric = ""
		is_float = ""

		if is_numeric:
			minimum_value = column.min()
			maximum_value = column.max()

			value = float(f"{value:.2f}")

