#
# (C) Copyright 2014-2023 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import sys
import importlib
from importlib.abc import MetaPathFinder, Loader

from . import _winerrors  # noqa

# Setup module redirection based on the backend
try:
    import cffi
except ImportError:
    _backend = 'ctypes'
else:
    del cffi
    _backend = 'cffi'


class BackendLoader(Loader):

    def __init__(self, redirect_module):
        self.redirect_module = redirect_module

    def load_module(self, fullname):
        module = importlib.import_module(self.redirect_module)
        sys.modules[fullname] = module
        return module


class BackendFinder(MetaPathFinder):

    def __init__(self, modules):
        self.redirected_modules = {
            'win32ctypes.core.{}'.format(module)
            for module in modules}

    def find_spec(self, fullname, path, target=None):
        if fullname in self.redirected_modules:
            module_name = fullname.split('.')[-1]
            if _backend == 'ctypes':
                redirected = f'win32ctypes.core.ctypes.{module_name}'
            else:
                redirected = f'win32ctypes.core.cffi.{module_name}'
            loader = BackendLoader(redirected)
            return importlib.machinery.ModuleSpec(module_name, loader)
        else:
            return None


sys.meta_path.append(BackendFinder([
    '_dll', '_authentication', '_time',
    '_common', '_resource', '_nl_support',
    '_system_information']))
