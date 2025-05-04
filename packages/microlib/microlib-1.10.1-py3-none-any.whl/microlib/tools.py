# -*- coding: utf-8 -*-

# Microlib is a small collection of useful tools.
# Copyright 2020 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Microlib.

# Microlib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Microlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Microlib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from itertools import zip_longest

from .deprecation import Deprecated


def rotate(L, n=1):
    """Rotate list L of n places, to the right if n > 0; else to the left."""
    return L[-n:] + L[:-n]


def grouper(iterable, n, padvalue=None):
    """
    grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')
    """
    # Taken from https://stackoverflow.com/a/312644/3926735
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)


@Deprecated(use_instead='pathlib.Path.read_text',
            extra_msg='pathlib.Path.read_text cannot concatenate, but it is '
            'easy to achieve via \'\\n\'.join([...]).',
            ref_url='https://docs.python.org/3/library/pathlib.html'
            '#pathlib.Path.read_text')
def read_text(*filenames, **kwargs):
    """
    Read and concatenate text from provided files.

    Encoding and separator can be provided as 'encoding' and 'sep' kwargs.
    """
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


def fracdigits_nb(d):
    return max(0, -d.as_tuple().exponent)


def turn_to_capwords(name):
    return ''.join(x.capitalize() for x in name.split('_'))
