from ctypes import *
from .utils import find_file

lib = cdll.LoadLibrary(find_file("display_status.so", "."))

# define class GoString to map:
# C type struct { const char *p; GoInt n; }
class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]

# define class GoSlice to map to:
# C type struct { void *data; GoInt len; GoInt cap; }
class GoSlice(Structure):
    _fields_ = [("data", POINTER(GoString)), ("len", c_longlong), ("cap", c_longlong)]

def to_go_string(url):
    url = bytes(url, 'utf-8')
    return GoString(url, len(url.decode()))

def to_go_slice(*urls):
    return GoSlice((GoString * len(urls))(*urls), len(urls), len(urls))

lib.DisplayLinks.argtypes = [GoSlice]
lib.DisplayLinks.restype = c_longlong
def display_status(*urls):
    urls = [to_go_string(url) for url in urls]
    lib.DisplayLinks(to_go_slice(*urls))
