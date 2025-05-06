'''
:date: Created on 12 mai 2022
:author: Voillat F.
'''
from .common import LASTNUM_RE, RANGE_SEP_CHAR, EXCLUSION_CHAR, SIZE_CHAR, RANGE_CHAR
from itertools import islice


class SerialNumber(object):
    '''Class representing a serial number.

    Args:
        sn_or_prefix (str): Serial number or serial number prefix. If *number* and *suffix* are :code:`None`, then this parameter is interpreted as a string describing a serial number.
        number (int): The number (default = None)
        suffix (str): Serial number suffix (default = None)
        padSize (int): Minimum digit group size (default = 1)
        padChar (str): Filler character for digit group (default = '0')

    A serial number consists of 3 parts:

    - The prefix: all the characters located before the last group of digits (number)
    - The number: the last group of digits, this part can be incremented
    - The suffix: all the characters located after the last group of digits (number)



    ====== ====== ====== ======
    String Prefix Number Suffix
    ====== ====== ====== ======
    A001X  A      1      X
    001X   None   1      X
    A001   A      1      None
    A12X01 A12X   1      None
    ====== ====== ====== ======


    '''

    @classmethod
    def explode(cls, s):
        '''Decomposes the string of characters into three constituent parts of a serial number.

        Args:
            s (str): String describing the serial number.

        Returns:
            tuple: A 3-tuple of containing the prefix, number, and suffix.

         The 3 elements of a serial number are:

         - The *prefix*: all the characters located before the last group of digits
         - The *number*: the last group of digits
         - The *suffix*: all the characters located after the last group of digits


        See also: :py:data:`.LASTNUM_RE`
        See also: The grammar rule for :a4:r:`serial number <serialnumbers.sn>`.

        >>> SerialNumber.explode('abc123-0045Z')
        ('abc123-', 45, 'Z', 4)

        >>> SerialNumber.explode('0045')
        (None, 45, None, 4)

        >>> SerialNumber.explode('abc123-0045')
        ('abc123-', 45, None, 4)

        >>> SerialNumber.explode('0045Z')
        (None, 45, 'Z', 4)
        '''
        m = LASTNUM_RE.search(s)
        try:
            return (m[1], int(m[2]), m[3], len(m[2]))
        except:
            raise ValueError(f'The string `{s!s}` does not correspond to a serial number!')


    @classmethod
    def fromString(cls, s):
        '''Creates a `SerialNumber` object from a string.

        Args:
            s (str): The serial number as a character string.

        Returns:
            SerialNumber: The created serial number.

        See also the grammar rule for :a4:r:`serial number <serialnumbers.sn>`.

        >>> str(SerialNumber.fromString('abc123-0045Z'))
        'abc123-0045Z'

        '''
        return SerialNumber(*SerialNumber.explode(s))


    @classmethod
    def listFromString(cls, s, inc=1, sep=RANGE_SEP_CHAR):
        '''Reads a character string containing the definition of one or more serial number ranges.

        Args:
            s (str): the character string containing the definition of the serial number ranges
            inc (int): The increment to compute numbers, default = 1
            sep (str): Serial number ranges separator character (default = :data:`.RANGE_SEP_CHAR`)



        See also the grammar rules for :a4:r:`lists <serialnumbers.list>` and for :a4:r:`exclusion ranges <serialnumbers.range>`


        >>> SerialNumber.listFromString('X01:10;X50-X59;-X02:2')
        [SerialNumber('X01'), SerialNumber('X04'), ..., SerialNumber('X10'), SerialNumber('X50'), ..., SerialNumber('X59')]
        '''
        ret = set()
        if s is None or s == '':
            return []
        for s0 in s.split(sep):
            s0 = s0.strip()
            if s0[0] == EXCLUSION_CHAR:
                ret -= set(SerialNumberRange.fromString(s0[1:], inc=inc))
            else:
                ret |= set(SerialNumberRange.fromString(s0, inc=inc))

        ret = list(ret)
        ret.sort()
        return ret

    @classmethod
    def compare(cls, a, b):
        '''Compare two serial numbers

        :param SerialNumber a: The reference serial number
        :param SerialNumber b: The serial number to compare
        :return: -1, if `a` < `b` ; 0, if `a` == `b`, 1 otherwise

        >>> SerialNumber.compare(SerialNumber('X02'), SerialNumber('X01'))
        1

        '''
        return a.cmp(b)

    def __init__(self, sn_or_prefix, number=None, suffix=None, padSize=1, padChar='0'):
        '''Constructor'''
        self.padChar = padChar
        if number is None and suffix is None:
            self.prefix, self.number, self.suffix, self.padSize = self.explode(sn_or_prefix)
        else:
            self.prefix = sn_or_prefix
            self.number = number
            self.suffix = suffix
            self.padSize = padSize



    def __repr__(self):
        '''Represents the serial number as a string.

        >>> SerialNumber('abc123-0045Z')
        SerialNumber('abc123-0045Z')

        :return: the serial number as a string.
        '''
        try:
            return '{:s}(\'{:s}\')'.format(self.__class__.__name__, self.toString())
        except:
            return super().__repr__()

    def __str__(self):
        '''Converts the serial number as a string.
        :return: the serial number as a string.
        '''
        try:
            return self.toString()
        except:
            return super().__str__()

    def __hash__(self):
        return hash(str(self))


    def __lt__(self, other):
        '''Checks if itself is lower than the other serial number.

        :param SerialNumber other: the other serial number.
        :return: `True`, if itself is less than the other serial number ; `False`, otherwise

        >>> SerialNumber('abc123-0045Z') < SerialNumber('abc123-', 46, 'Z', 4)
        True
        '''

        assert isinstance(other, SerialNumber), 'The other object isn\'t a SerialNumber!'
        if self.inSameRange(other):
            return self.number < other.number
        else:
            return self.toString() < other.toString()

    def __eq__(self, other):
        '''Checks if itself is equal to the other serial number.

        :param SerialNumber other: the other serial number.
        :return: `True`, if itself is equal to the other serial number

        >>> SerialNumber('abc123-0045Z') == SerialNumber('abc123-', 45, 'Z', 4)
        True
        '''
        return self.inSameRange(other) and self.number == other.number

    def inSameRange(self, other):
        '''Checks if itself is in the same range as the other serial number.

        Two serial numbers are considered to be from the same range if their prefixes and suffixes are the same.

        :param SerialNumber other: the other serial number.
        :return: `True`, if itself is in the same range as the other serial number.

        >>> SerialNumber('abc123-0045Z').inSameRange(SerialNumber('abc123-', 102, 'Z', 4))
        True
        >>> SerialNumber('abc123-0045X').inSameRange(SerialNumber('abc123-', 102, 'Z', 4))
        False
        '''
        assert isinstance(other, SerialNumber), 'The other object isn\'t a SerialNumber!'
        return self.prefix == other.prefix and self.suffix == other.suffix

    def isNext(self, other, inc=1):
        '''Checks if the other serial number is the next.

        :param SerialNumber other: the other serial number.
        :return: `True`, if the other serial number is the next.

        >>> SerialNumber('abc123-0044Z').isNext(SerialNumber('abc123-', 45, 'Z', 4))
        True
        '''
        return self.inSameRange(other) and self.number+inc == other.number

    def toString(self):
        '''Returns the serial number as a string.

        :return: the serial number as a string.

        >>> SerialNumber(None, number=123, suffix='A', padSize=5, padChar='#').toString()
        '##123A'

        '''
        n = str(self.number)
        return (self.prefix or '') + self.padChar*(self.padSize-len(n)) + n + (self.suffix or '')

    def next(self, inc=1):
        '''Returns the next serial number

        :param int inc: Increment to compute the next serial number
        :return: the next serial number according increment.
        :rtype: SerialNumber

        >>> SerialNumber('abc123-0044Z').next(2)
        SerialNumber('abc123-0046Z')
        '''
        if inc == -1:
            return self
        else:
            return SerialNumber(self.prefix, self.number+inc, self.suffix, self.padSize, self.padChar);

    def prev(self, inc=1):
        '''Returns the previous serial number

        :param int inc: Increment to compute the next serial number
        :return SerialNumber: the previous serial number according increment.

        >>> SerialNumber('x0044Z').prev(2)
        SerialNumber('x0042Z')
        '''
        if self.number==0:
            raise ValueError('No previous serial number!');
        return SerialNumber(self.prefix, self.number-inc, self.suffix, self.padSize, self.padChar);

    def countTo(self, other, inc=1):
        '''Counts the number of SNs in the interval with another SN

        Both serial numbers must be in the same range (see :py:meth:`~.SerialNumber.inSameRange`).

        :param SerialNumber other: The other serial number
        :param int inc: Increment
        :return: The number of SNs in the interval with the other SN.

        >>> SerialNumber('x001Z').countTo(SerialNumber('x020Z'))
        20

        >>> SerialNumber('x001Z').countTo(SerialNumber('y020Z'))
        Traceback (most recent call last):
        ...
        ValueError: The other serial number (y020Z) is not in the same range (x001Z)!

        '''
        assert isinstance(other, SerialNumber), 'The other object isn\'t a SerialNumber!'
        if not self.inSameRange(other):
            raise ValueError('The other serial number ({0!s}) is not in the same range ({1!s})!'.format(other, self))
        return (1 + other.number - self.number) // inc


    def genCount(self, count, inc=1):
        '''Returns a generator for a list of `count` serial numbers.

        >>> print(list(SerialNumber('x001Z').genCount(10)))
        [SerialNumber('x001Z'), SerialNumber('x002Z'), ..., SerialNumber('x010Z')]
        '''
        current = self
        for _ in range(int(count)):
            yield current
            current = current.next(inc)

    def genEnd(self, end, inc=1):
        '''Returns a generator for a list of serial numbers according the `end`.

        >>> print(list(SerialNumber('x001Z').genEnd(SerialNumber('x020Z'))))
        [SerialNumber('x001Z'), SerialNumber('x002Z'), ..., SerialNumber('x020Z')]
        '''
        current = self
        yield current
        while current < end:
            current = current.next(inc);
            yield current

    def range(self, a, b=None, c=1):
        '''Creates a range of serial numbers

        :param int a : If `b` isn't defined the stop index of the range, then the star index
        :param int b : If defined, the stop index of the range
        :param int c : Step (increment) to compute serial number

        >>> list(SerialNumber('x010Z').range(10))
        [SerialNumber('x010Z'), SerialNumber('x011Z'), ..., SerialNumber('x019Z')]

        >>> list(SerialNumber('x010Z').range(2,5))
        [SerialNumber('x012Z'), SerialNumber('x013Z'), ..., SerialNumber('x015Z')]

        '''
        if b is None:
            return SerialNumberRange(self, a, None, c)
        else:
            return SerialNumberRange(self.next(a), None, self.next(b), c)

    def cmp(self, other):
        '''Compare two serial numbers

        :param SerialNumber other: the other serial number
        :return: -1, if `other` is smaller ; 0, if both are equal ; 1 otherwise.

        >>> SerialNumber('x001Z').cmp(SerialNumber('x001Z'))
        0

        >>> SerialNumber('x001Z').cmp(SerialNumber('x002Z'))
        -1

        >>> SerialNumber('x001Z').cmp(SerialNumber('a001Z'))
        1
        '''
        if self == other:
            return 0
        elif self < other:
            return -1
        return 1





class SerialNumberRange(object):
    '''Class representing a range of serial numbers

    A serial number range consists of a sequence of consecutive serial numbers

    Args:
        first (SerialNumber): The first serial number of range
        count (int): If defined, the size of range
        last (SerialNumber): If defined, the last serial number of range
        inc (int): The increment to compute numbers, default = 1

    '''

    EXCLUDE = False

    @classmethod
    def fromStartEnd(cls, first, last, inc=1):
        return SerialNumberRange(first, None, last, inc)
    @classmethod
    def fromStartCount(cls, first, count, inc=1):
        return SerialNumberRange(first, count, None, inc)
    @classmethod
    def fromString(cls, s, inc=1):
        '''Creates a range of serial numbers from a string.

        Args:
            s (str): The string describing the serial number range
            inc (int): The increment to compute numbers, default = 1

        Returns:
            SerialNumberRange, SerialNumberXRange: The created serial numbers range or exclusion range

        A serial number range is defined by giving the starting and ending serial numbers separated
        by a hyphen (-), or by giving the starting serial number and the number of numbers separated
        by a colon (:).
        If the range definition string starts with a hyphen (-), then it is an exclusion range and will
        result in an object of class :class:`SerialNumberXRange`.


        See also the grammar rule for :a4:r:`lists <serialnumbers.range>`

        >>> list(SerialNumberRange.fromString('X001:10'))
        [SerialNumber('X001'), SerialNumber('X002'), ..., SerialNumber('X010')]

        >>> list(SerialNumberRange.fromString('X001-X010'))
        [SerialNumber('X001'), SerialNumber('X002'), ..., SerialNumber('X010')]

        >>> list(SerialNumberRange.fromString('X001'))
        [SerialNumber('X001')]

        >>> SerialNumberRange.fromString('-X05:2')
        SerialNumberXRange('-X05-X06')


        '''


        if s[0] == EXCLUSION_CHAR:
            cls = SerialNumberXRange
            s = s[1:]
        if SIZE_CHAR in s:
            start, count = s.split(SIZE_CHAR,2)
            return cls(SerialNumber(start), int(count), inc=inc)
        elif RANGE_CHAR in s:
            start, end = s.split(RANGE_CHAR,2)
            return cls(SerialNumber(start), None, SerialNumber(end), inc=inc)
        else:
            return cls(SerialNumber(s), 1, inc=inc)



    def __init__(self, first, count=None, last=None, inc=1):
        assert isinstance(first, SerialNumber), 'The `first` argument must be a SerialNumber ({!s})!'.format(type(first).__name__)
        self._first = first
        self._inc = inc
        if count is None:
            assert isinstance(last, SerialNumber), 'If `count` is None, then the `last` argument must be a SerialNumber!'
            self._last = last
            self._count = self._first.countTo(self._last, self._inc)
        elif count == 1:
            self._count = 1
            self._last = self._first
        else:
            self._count = count
            self._last = self._first.next((self._count-1)*self._inc)

    def __str__(self):
        '''Converts the serial number range as a string.

        Returns
            str: The serial number range as a string.

        >>> str(SerialNumberRange(SerialNumber('X0123'), 5))
        'X0123-X0127'
        '''
        try:
            return self.toString()
        except:
            return super().__str__()

    def __repr__(self):
        '''Represents the serial number range as a string.

        Returns
            str: The serial number as a string.

        >>> SerialNumberRange(SerialNumber('X001'), None, SerialNumber('X010'))
        SerialNumberRange('X001-X010')
        '''

        try:
            return '{:s}(\'{:s}\')'.format(self.__class__.__name__, self.toString())
        except:
            return super().__repr__()

    def __len__(self):
        return self._count

    def __getitem__(self, key):
        '''
        >>> SerialNumberRange(SerialNumber('X001'), 10)[5]
        SerialNumber('X005')

        >>> SerialNumberRange(SerialNumber('X001'), 10)[2:5]
        [SerialNumber('X003'), SerialNumber('X004'), SerialNumber('X005')]

        '''
        if isinstance(key, int):
            if key < 0 or key > self._count:
                raise IndexError
            return self._first.next((key-1)*self._inc)
        else:
            return list(self)[key]

    def __iter__(self):
        '''
        >>> list(SerialNumberRange(SerialNumber('X001'), 10))
        [SerialNumber('X001'), ..., SerialNumber('X010')]
        '''
        current = self._first
        for _ in range(self._count):
            yield current
            current = current.next(self._inc)


    def __contains__(self, sn_or_range):
        '''Determines whether an SN or a range of SNs is contained in a range of SNs.

        Args:
            sn_or_range (SerialNumber,SerialNumberRange):

        Returns:
            bool: True, if `sn_or_range` is in `self` ; False, otherwise

        >>> SerialNumber('X05') in SerialNumberRange.fromString('X01:10')
        True

        >>> SerialNumber('X12') in SerialNumberRange.fromString('X01:10')
        False

        >>> SerialNumber('Y05') in SerialNumberRange.fromString('X01:10')
        False

        >>> SerialNumber('X04') in SerialNumberRange.fromString('X00:10', inc=2)
        True

        >>> SerialNumber('X05') in SerialNumberRange.fromString('X00:10', inc=2)
        False

        >>> SerialNumberRange.fromString('X01:5') in SerialNumberRange.fromString('X01:10')
        True

        >>> SerialNumberRange.fromString('X07:5') in SerialNumberRange.fromString('X01:10')
        False

        >>> SerialNumberRange.fromString('X01:5') in SerialNumberRange.fromString('X01:10', inc=2)
        False
        '''

        if isinstance(sn_or_range, SerialNumber):
            return sn_or_range.inSameRange(self.first) \
                and self.first.number <= sn_or_range.number <= self.last.number \
                and (sn_or_range.number - self.first.number) % self._inc == 0
        elif isinstance(sn_or_range, SerialNumberRange):
            return sn_or_range.first.inSameRange(self.first) \
                and sn_or_range.inc == self._inc \
                and self.first.number <= sn_or_range.first.number \
                and sn_or_range.last.number <= self.last.number \
                and (sn_or_range.first.number - self.first.number) % self._inc == 0
        else:
            raise ValueError('The `sn_or_range` argument must be a SerialNumber or a SerialNumberRange!')



    def toStringFirstLast(self):
        '''Represents the serial number range in the format: A-B,
        where A and B are, respectively, the first and last serial number in the range

        Returns:
            str : The Representation of the serial number range in the format: A-B

        >>> SerialNumberRange(SerialNumber('X001'), 10).toStringFirstLast()
        'X001-X010'
        '''
        if self.count == 1:
            return self.first.toString()
        else:
            return self.first.toString() + RANGE_CHAR + self.last.toString()

    def toStringFirstCount(self):
        '''Represents the serial number range in the format: A:C,
        where A and C are, respectively, the first serial number and the number of serial numbers in the range

        Returns:
            str : The Representation of the serial number range in the format: A:C

        >>> SerialNumberRange(SerialNumber('X001'), 10).toStringFirstCount()
        'X001:10'
        '''
        if self.count == 1:
            return self.first.toString()
        else:
            return self.first.toString() + SIZE_CHAR + str(self.count)

    def toString(self):
        return self.toStringFirstLast()


    @property
    def first(self):
        return self._first
    @property
    def last(self):
        return self._last
    @property
    def count(self):
        return self._count
    @property
    def inc(self):
        return self._inc

class SerialNumberXRange(SerialNumberRange):
    EXCLUDE = True

    def toStringFirstLast(self):
        '''
        >>> str(SerialNumberXRange.fromString('X01:3'))
        '-X01-X03'
        '''

        return EXCLUSION_CHAR + SerialNumberRange.toStringFirstLast(self)

    def toStringFirstCount(self):
        return EXCLUSION_CHAR + SerialNumberRange.toStringFirstCount(self)


class SerialNumberList(object):
    '''Class for a list of serial number ranges.

    Args:
        snlist (str or list): Characters string containing the definition of one or more serial number ranges or list of :class:`SerialNumber` or :class:`SerialNumberRange`.
        inc (int): The increment to compute numbers, default = 1
        sep (str): Serial number ranges separator character (default = :data:`.RANGE_SEP_CHAR`)

    .. note::
        If `snlist` is a list, then all elements must be of the same class, either :class:`SerialNumber` or :class:`SerialNumberRange`.


    >>> list(SerialNumberList('X01:10;X50-X59;-X02:2').ranges)
    [SerialNumberRange('X01'), SerialNumberRange('X04-X10'), SerialNumberRange('X50-X59')]

    '''
    @classmethod
    def snListFromString(cls, s, inc=1, sep=RANGE_SEP_CHAR):
        '''Reads a string containing the definition of one or more serial number ranges and convert it into a list of SNs.

        Args:
            s (str): Characters string containing the definition of one or more serial number ranges.
            inc (int): The increment to compute numbers, default = 1
            sep (str): Serial number ranges separator character (default = :data:`.RANGE_SEP_CHAR`)

        Returns:
            SerialNumberList: The created list of serial numbers ranges
        '''
        temp = set([])
        if not(s is None or s == ''):
            for s0 in s.split(sep):
                s0 = s0.strip()
                if s0[0] == EXCLUSION_CHAR:
                    temp -= set(SerialNumberRange.fromString(s0[1:], inc=inc))
                else:
                    temp |= set(SerialNumberRange.fromString(s0, inc=inc))

            temp = list(temp)
            temp.sort()

        return temp

    @classmethod
    def snRangesFromList(cls, snlist, inc=1, nosort=False):
        '''Convert a list of SN to a list of SN ranges

        Args:
            snlist (list,tuple): The list of serial numbers to convert
            inc (int): The increment to compute numbers, default = 1

        Returns:
            list: The list of SerialNumberRange


        >>> list(SerialNumberList.snRangesFromList(SerialNumber.listFromString('X01:10;X50-X59;-X02:2')))
        [SerialNumberRange('X01'), SerialNumberRange('X04-X10'), SerialNumberRange('X50-X59')]
        '''
        l = len(snlist)
        if not nosort:
            snlist.sort()
        if l == 0:
            return []
        elif l == 1:
            return [SerialNumberRange(snlist[0], count=1, inc=inc)]

        ret = []
        sn0 = sn1 = snlist[0]
        for sn2 in snlist[1:]:
            if not sn1.isNext(sn2, inc=inc):
                ret.append(SerialNumberRange(sn0, last=sn1, inc=inc))
                sn0 = sn2
            sn1 = sn2
        ret.append( SerialNumberRange(sn0, last=sn1, inc=inc))
        return ret

    def __init__(self, snlist=None, inc=1, sep=RANGE_SEP_CHAR):
        '''Constructor'''
        self._sep = sep
        self._inc = inc
        self._ranges = []
        self._numbers = None

        if isinstance(snlist, str) and snlist != '':
            self._ranges = [ SerialNumberRange.fromString(r.strip(), inc=inc) for r in snlist.split(self._sep) ]
        elif isinstance(snlist, (list,tuple)) and len(snlist)>0:
            if isinstance(snlist[0], SerialNumber):
                self._ranges = self.snRangesFromList(snlist, inc=inc)
            elif isinstance(snlist[0], SerialNumberRange):
                self._ranges = snlist
        else:
            pass
        self._update()




    def _update(self):
        temp = set([])
        e = []
        for r in self._ranges:
            if r.EXCLUDE:
                e.append(r)
            else:
                temp |= set(r)
        for r in e:
            temp -= set(r)
        self._numbers = list(temp)
        self._numbers.sort()
        self._ranges = self.snRangesFromList(self._numbers, inc=self._inc, nosort=True)

    def __getitem__(self, key):
        return self._numbers[key]

    def __iter__(self):
        for sn in self._numbers:
            yield sn

    def __len__(self):
        return len(self._numbers)

    def __str__(self):
        '''Converts the list of serial numbers as a string.

        Returns:
            str: A character string containing the definition of one or more serial number ranges.

        '''
        try:
            return self.toString()
        except:
            return super().__str__()

    def __repr__(self):
        '''Represents the serial number range as a string.

        Returns:
            str: The serial number as a string.
        '''

        try:
            #return RANGE_SEP_CHAR.join( [repr(r) for r in self] )
            return '{:s}(\'{!s}\')'.format(self.__class__.__name__, self.toString())
        except:
            return super().__repr__()

    def getNumbers(self):
        if self._numbers is None:
            temp = set([])
            e = []
            for r in self._ranges:
                if r.EXCLUDE:
                    e.append(r)
                else:
                    temp |= set(r)
            for r in e:
                temp -= set(r)
            self._numbers = list(temp)
            self._numbers.sort()

        return self._numbers

    def toString(self):
        return RANGE_SEP_CHAR.join( [r.toString() for r in self._ranges] )


    def addNumber(self, sn):
        '''Add a serial number into ranges list.

        Args:
            sn (SerialNumber): SN to addRange.
        '''
        self.addRange(SerialNumberRange(sn, count=1, inc=self._inc))

    def clear(self):
        self._numbers = []
        self._ranges = []

    def addRange(self, snRange, force=False):
        '''Add a serial number range into the list.

        Args:
            snRange (SerialNumberRange) : The range to add
            force (bool) : If true, forces the addition even if one or more SNs are already in the list.
                Otherwise the exception ValueError is issued.

        >>> SerialNumberList('X01:5;X10:5').addRange(SerialNumberRange.fromString('X06:4')).ranges
        [SerialNumberRange('X01-X14')]
        '''
        assert isinstance(snRange, SerialNumberRange)
        self._ranges.append(snRange)
        self._update()
        return self
    
    
    def addList(self, snList):
        '''Add a serial number list into the list.
        
        Args:
            snList (SerialNumberList): The list to  add.
            
        >>> SerialNumberList('X01:5').addList(SerialNumberList('X06:5')).ranges
        [SerialNumberRange('X01-X10')]
        '''
        assert isinstance(snList, SerialNumberList)
        for r in snList.ranges:
            self._ranges.append(r)
        self._update()
        return self 
    
    
    def groupby(self, n):
        '''Splits serial numbers into groups of `n` elements in a list of class:`SeriaNumberList`.
        
        Args:
            n (int): is the number of issues per group.
            
        Returns:
            (list) : A list of `SeriaNumberList`.
        
        >>> SerialNumberList('X01:20').groupby(10)
        [SerialNumberList('X01-X10'), SerialNumberList('X11-X20')]
        >>> SerialNumberList('X01:20').groupby(6)
        [SerialNumberList('X01-X06'), ..., SerialNumberList('X13-X18'), SerialNumberList('X19-X20')]
        '''
        it = iter(self) 
        ret = [SerialNumberList(list(islice(it, n))) for _ in range((len(self) + n - 1) // n)]
        return ret
        

    @property
    def inc(self):
        return self._inc

    @property
    def numbers(self):
        return self.getNumbers()

    @property
    def ranges(self):
        return self._ranges
