'''

:author:  F. Voillat
:date: 2022-05-23 Creation
:copyright: Dassym SA 2021
'''

import re as RE


LASTNUM_RE = RE.compile(r"(.*\D)?(\d+)(\D+)?")
'''Regex to decompose a serial number'''

RANGE_CHAR = '-'
'''Char to separate the first and last serial numbers of range'''

SIZE_CHAR = ':'
'''Char to separate the first serial number and the size of range'''

RANGE_SEP_CHAR  = ';'
'''Default char to separate the two ranges'''

EXCLUSION_CHAR = '-'
'''Char to specify an exclusion range'''
