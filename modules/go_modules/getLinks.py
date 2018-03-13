from ctypes import cdll, c_char_p, c_longlong, c_int, Structure
import sys

goBot = cdll.LoadLibrary("./goBot.so")


class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]


goBot.GetLinks.argtypes = [GoString, GoString, GoString, c_int]
url = sys.argv[1].encode('utf-8')
addr = b"127.0.0.1"
port = b"9050"
goBot.GetLinks(GoString(url, len(url)),
               GoString(addr, len(addr)),
               GoString(port, len(port)),
               15)
