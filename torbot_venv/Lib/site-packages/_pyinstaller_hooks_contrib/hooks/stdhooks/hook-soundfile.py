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
pysoundfile:
https://github.com/bastibe/SoundFile
"""

import os

from PyInstaller.compat import is_win, is_darwin
from PyInstaller.utils.hooks import get_module_file_attribute

# get path of soundfile
module_dir = os.path.dirname(get_module_file_attribute('soundfile'))

# add binaries packaged by soundfile on OSX and Windows
# an external dependency (libsndfile) is used on GNU/Linux
path = None
if is_win:
    path = os.path.join(module_dir, '_soundfile_data')
elif is_darwin:
    path = os.path.join(module_dir, '_soundfile_data', 'libsndfile.dylib')

if path is not None and os.path.exists(path):
    binaries = [(path, "_soundfile_data")]
