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
in sys.path for file pywintypesXX.dll. Include the pywintypesXX.dll
as a data file. The path to this dll is contained in __file__
attribute.
"""

from PyInstaller.utils.hooks import get_pywin32_module_file_attribute

_pth = get_pywin32_module_file_attribute('pywintypes')
binaries = [(_pth, '.')]
