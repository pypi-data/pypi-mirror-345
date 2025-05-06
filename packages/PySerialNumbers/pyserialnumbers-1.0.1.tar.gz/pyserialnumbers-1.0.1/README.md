# PySerialNumbers
The *PySerialNumbers* library offers functionalities for manipulating serial numbers.
In particular the possibility of reading a character string formatted according to the ad hoc grammar,
then of converting it into a list of serial numbers.

Version: 1.0.1 (2025-05-05)

This program is free software: you can redistribute it and/or modify
it under the terms of the **GNU General Public License** as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You can consult the GNU General Public License on <http://www.gnu.org/licenses/gpl-3.0.html>.


## Install

This installs a package that can be used from *Python* (`import serialnumbers`).

To install for all users on the system, administrator rights (root) may be required.

*PySerialNumbers* library requires [Python](https://www.python.org) 3.4 or later.

### From PyPI

*PySerialNumbers* can be installed from PyPI:

> python -m pip install PySerialNumbers

Use `python` or `python3` depending on your system.
Usually `python` on a *Windows* system and `python3` on a *GNU/Linux* system.


### From source

Download the archive from <https://github.com/dassym/PySerialNumbes/releases>.
Unpack the archive, enter the PySerialNumbers-x.y.z directory and run:

> python -m pip install -e ./

Use `python` or `python3` depending on your system.
Usually `python` on a *Windows* system and `python3` on a *GNU/Linux* system.

## Documentation

You can find the documentation on  <https://pyserialnumbers.readthedocs.io/en/latest/>.

### Usage samples

This example shows how to create a list of 20 serial numbers from `SN01` to `SN20` according a string defining this list.

	import serialnumbers
	list(serialnumbers.SerialNumberList('SN01-SN10'))

The same example but with a different way of describing the list.

	list(serialnumbers.SerialNumberList('SN01:20'))

This example shows how to create a list of 16 serial numbers from `SN01` to `SN04` and `SN09` to `SN20` .

	list(serialnumbers.SerialNumberList('SN01-SN20;-SN05:4'))

The serial number list ad hoc grammar is described bellow according [ANTLR](https://github.com/antlr/antlr4/blob/master/doc/index.md) notation.

	/**
	 * Grammar to define one or more serial numbers.
	 */

	grammar serialnumbers;

	/**
	 * List of serial numbers ranges
	 */
	list : range ( ';' range )* ;

	/**
	 * Range of serial numbers.
	 */
	range : '-'? sn ( '-' sn | ':' DIGIT+ )? ;

	/**
	 * serial number.
	 */
	sn : ALPHANUM* DIGIT+ ALPHA* ;

	/**
	 * Digit characters
	 */
	DIGIT : [0-9] ;

	/**
	 * Alphabetic characters
	 */
	ALPHA : [A-Za-z] | '+' | '/' | '*' | '.' | ',' | '$' | '#' | '@' | '~' | '_' ;

	/**
	 * Alphabetic and numeric characters
	 */
	ALPHANUM : ALPHA | DIGIT ;



