import datetime as DT

MAJOR_VERSION = 1
'''Major version number'''

MINOR_VERSION = 0
'''Minor version number'''

REVISION_VERSION = 1
'''Revision version number'''

VERSION = (MAJOR_VERSION, MINOR_VERSION, REVISION_VERSION)
'''Version number as 3-tuples containing *major*, *minor* and *revision* numbers.''' 

__version__ = '{0:d}.{1:d}.{2:d}'.format(*VERSION)
'''Application version number'''

__ver__ = '{0:d}.{1:d}'.format(*VERSION)
'''Application short version number'''

DATE = DT.date(2025, 5, 5)
'''Release date'''

REQUIRED_PYTHON = (3,4)
'''The required Python verison'''
