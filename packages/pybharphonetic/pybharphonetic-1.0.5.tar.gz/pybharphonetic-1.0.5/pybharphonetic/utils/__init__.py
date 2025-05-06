#!/usr/bin/env python

"""Python implementation of the any Indian language to phonetic software.

-------------------------------------------------------------------------------
Copyright (C) 2023 Subrata Sarkar <subrotosarkar32@gmail.com>
modified by:- Subrata Sarkar <subrotosarkar32@gmail.com>

This file is part of pybharphonetic.

pybharphonetic is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pybharphonetic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pybharphonetic.  If not, see <http://www.gnu.org/licenses/>.

"""

# Imports
import sys


def utf(text):
    """Shortcut funnction for encoding given text with utf-8."""
    if sys.version_info.major <= 2:
        try:
            output = unicode(text, encoding='utf-8')
        except UnicodeDecodeError:
            output = text
        except TypeError:
            output = text
        return output
    else:
        return text
