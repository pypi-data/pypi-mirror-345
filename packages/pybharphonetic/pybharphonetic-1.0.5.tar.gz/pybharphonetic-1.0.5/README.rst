

pybharphonetic
=================
Python implementation of the any Indian language to phonetic software

License
=======

Copyright (C) 2023 Subrata Sarkar <subrtosarkar32@gmail.com>.

::

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
    along with pyhinavrophonetic. If not, see <http://www.gnu.org/licenses/>.

The full license text can be found in ``LICENSE``.

Usage
=====

::


      from pybharphonetic import bharphonetic
      bharphonetic.parse("kese hO?", language="hn")


Supported Languages
===================

::
    
    "hn": "hindi",
    "bn": "bengali",
    "as": "assamese",
    "bd": "bodo",
    "dg": "dogri",
    "gj": "gujrati",
    "kn": "kannada",
    "ks": "kashmiri",
    "kon": "konkani",
    "mai": "maithili",
    "mal": "malayalam",
    "man": "manipuri",
    "mar": "marathi",
    "nep": "nepali",
    "odi": "odia",
    "pun": "punjabi",
    "sak": "sanskrit",
    "san": "santhali",
    "sin": "sindhi",
    "tam": "tamil",
    "tel": "telugu",
    "urd": "urdu"

Overview
========

Python implementation of the english phonetic to any Indian language software

Installation
============

Using Git:

::

    $ git clone https://github.com/SubrataSarkar32/pybharphonetic
    $ cd pybharphonetic
    $ sudo python3 setup.py install


Using Pip:

::

    $ sudo pip install pybharphonetic


Usage
=====

At present only a subset of features have been implemented. When
implemented, the parser can be accessed as:

::

    >>> from pybharphonetic import bharphonetic
    >>> bharphonetic.parse("kese hO?", language="hn")

Contributing
============

**Fork** -> **Do your changes** -> **Send a Pull Request**. It's that
easy!

Coding style follows `PEP 8`_ along with `PEP 257`_ for Docstring
conventions.

Also, if you find any bugs, please report them in the Issues queue. As
always, before you report any new issue, please check that it has not
been already posted by someone else.


Below is license of pyAvroPhonetic from which it has been derived:
==================================================================




pyhinavrophonetic
=================
Python implementation of the Hindi phonetic-typing software

License
=======

Copyright (C) 2016 Subrata Sarkar <subrtosarkar32@gmail.com>.

::

    This file is part of pyhinavrophonetic.

    pyhinavrophonetic is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyhinavrophonetic is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyhinavrophonetic. If not, see <http://www.gnu.org/licenses/>.

The full license text can be found in ``LICENSE``.
