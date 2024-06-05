#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
""" A module which supports common Windows types. """
import contextlib


class error(Exception):
    def __init__(self, *args, **kw):
        nargs = len(args)
        if nargs > 0:
            self.winerror = args[0]
        else:
            self.winerror = None
        if nargs > 1:
            self.funcname = args[1]
        else:
            self.funcname = None
        if nargs > 2:
            self.strerror = args[2]
        else:
            self.strerror = None
        Exception.__init__(self, *args, **kw)


@contextlib.contextmanager
def pywin32error():
    try:
        yield
    except WindowsError as exception:
        if not hasattr(exception, 'function'):
            exception.function = 'unknown'
        raise error(exception.winerror, exception.function, exception.strerror)
