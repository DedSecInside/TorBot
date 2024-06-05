# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------


"""
pywin32 module supports frozen mode. In frozen mode it is looking
in sys.path for file pythoncomXX.dll. Include the pythoncomXX.dll
as a data file. The path to this dll is contained in __file__
attribute.
"""

import os.path
from PyInstaller.utils.hooks import get_pywin32_module_file_attribute

_pth = get_pywin32_module_file_attribute('pythoncom')

# Binaries that should be included with the module 'pythoncom'.
binaries = [
    (
        # Absolute path on hard disk.
        _pth,
        # Relative directory path in the ./dist/app_name/ directory.
        '.',
    )
]
