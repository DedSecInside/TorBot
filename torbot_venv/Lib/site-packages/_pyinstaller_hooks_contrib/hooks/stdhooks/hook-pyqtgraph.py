# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# include all .ui and image files
datas = collect_data_files("pyqtgraph",
                           includes=["**/*.ui", "**/*.png", "**/*.svg"])

# pyqtgraph uses Qt-version-specific templates for the UI elements.
# There are templates for different versions of PySide and PyQt, e.g.
#
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt6
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyside2
# - pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyside6
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt6
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyside2
# - pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyside6
#
# To be future-proof, we include all of them via a filter in
# collect-submodules.
# Tested with pyqtgraph master branch (commit c1900aa).
hiddenimports = collect_submodules(
    "pyqtgraph", filter=lambda name: "Template" in name)
