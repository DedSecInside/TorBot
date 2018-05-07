import sys

from ctypes import cdll, c_char_p, c_longlong, c_int, Structure

getLinks = cdll.LoadLibrary("modules/lib/getLinks.so")

class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]

getLinks.GetLinks.argtypes = [GoString, GoString, GoString, c_int]

def GetLinks(url, addr, port, timeout):

    url = url.encode('utf-8')
    addr = addr.encode('utf-8')
    port = str(port).encode('utf-8')

    getLinks.GetLinks(GoString(url, len(url)),
                      GoString(addr, len(addr)),
                      GoString(port, len(port)),
                      timeout)
