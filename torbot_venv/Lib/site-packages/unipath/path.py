"""unipath.py - A two-class approach to file/directory operations in Python.

Full usage, documentation, changelog, and history are at
http://sluggo.scrapping.cc/python/unipath/

(c) 2007 by Mike Orr (and others listed in "History" section of doc page).
Permission is granted to redistribute, modify, and include in commercial and
noncommercial products under the terms of the Python license (i.e., the "Python
Software Foundation License version 2" at 
http://www.python.org/download/releases/2.5/license/).
"""

import errno
import fnmatch
import glob
import os
import shutil
import stat
import sys
import time
import warnings

from unipath.abstractpath import AbstractPath
from unipath.errors import RecursionError

__all__ = ["Path"]

#warnings.simplefilter("ignore", DebugWarning, append=1)

def flatten(iterable):
    """Yield each element of 'iterable', recursively interpolating 
       lists and tuples.  Examples:
       [1, [2, 3], 4]  =>  iter([1, 2, 3, 4])
       [1, (2, 3, [4]), 5) => iter([1, 2, 3, 4, 5])
    """
    for elm in iterable:
        if isinstance(elm, (list, tuple)):
            for relm in flatten(elm):
                yield relm
        else:
            yield elm

class Path(AbstractPath):

    ##### CURRENT DIRECTORY ####
    @classmethod
    def cwd(class_):
        """ Return the current working directory as a path object. """
        return class_(os.getcwd())

    def chdir(self):
        os.chdir(self)

    #### CALCULATING PATHS ####
    def absolute(self):
        """Return the absolute Path, prefixing the current directory if
           necessary.
        """
        return self.__class__(os.path.abspath(self))

    def relative(self):
        """Return a relative path to self from the current working directory.
        """
        return self.__class__.cwd().rel_path_to(self)

    def rel_path_to(self, dst):
        """ Return a relative path from self to dst.

        This prefixes as many pardirs (``..``) as necessary to reach a common
        ancestor.  If there's no common ancestor (e.g., they're are on 
        different Windows drives), the path will be absolute.
        """
        origin = self.__class__(self).absolute()
        if not origin.isdir():
            origin = origin.parent
        dest = self.__class__(dst).absolute()

        orig_list = origin.norm_case().components()
        # Don't normcase dest!  We want to preserve the case.
        dest_list = dest.components()

        if orig_list[0] != os.path.normcase(dest_list[0]):
            # Can't get here from there.
            return self.__class__(dest)

        # Find the location where the two paths start to differ.
        i = 0
        for start_seg, dest_seg in zip(orig_list, dest_list):
            if start_seg != os.path.normcase(dest_seg):
                break
            i += 1

        # Now i is the point where the two paths diverge.
        # Need a certain number of "os.pardir"s to work up
        # from the origin to the point of divergence.
        segments = [os.pardir] * (len(orig_list) - i)
        # Need to add the diverging part of dest_list.
        segments += dest_list[i:]
        if len(segments) == 0:
            # If they happen to be identical, use os.curdir.
            return self.__class__(os.curdir)
        else:
            newpath = os.path.join(*segments)
            return self.__class__(newpath)
    
    def resolve(self):
        """Return an equivalent Path that does not contain symbolic links."""
        return self.__class__(os.path.realpath(self))
    

    #### LISTING DIRECTORIES ####
    def listdir(self, pattern=None, filter=None, names_only=False):
        if names_only and filter is not None:
            raise TypeError("filter not allowed if 'names_only' is true")
        empty_path = self == ""
        if empty_path:
            names = os.listdir(os.path.curdir)
        else:
            names = os.listdir(self)
        if pattern is not None:
            names = fnmatch.filter(names, pattern)
        names.sort()
        if names_only:
            return names
        ret = [self.child(x) for x in names]
        if filter is not None:
            ret = [x for x in ret if filter(x)]
        return ret

    def walk(self, pattern=None, filter=None, top_down=True):
        return self._walk(pattern, filter, top_down=top_down, seen=set())

    def _walk(self, pattern, filter, top_down, seen):
        if not self.isdir():
            raise RecursionError("not a directory: %s" % self)
        real_dir = self.resolve()
        if real_dir in seen:
            return  # We've already recursed this directory.
        seen.add(real_dir)
        for child in self.listdir(pattern):
            is_dir = child.isdir()
            if is_dir and not top_down:
                for grandkid in child._walk(pattern, filter, top_down, seen):
                    yield grandkid
            if filter is None or filter(child):
                yield child
            if is_dir and top_down:
                for grandkid in child._walk(pattern, filter, top_down, seen):
                    yield grandkid
                

    #### STAT ATTRIBUTES ####
    exists = os.path.exists
    lexists = os.path.lexists

    isfile = os.path.isfile
    
    def isdir(self):
        return os.path.isdir(self)
    
    islink = os.path.islink
    ismount = os.path.ismount

    atime = os.path.getatime
    ctime = os.path.getctime
    mtime = os.path.getmtime

    size = os.path.getsize

    if hasattr(os.path, 'samefile'):
        same_file = os.path.samefile

    # For some reason these functions have to be wrapped in methods.
    def stat(self):
        return os.stat(self)

    def lstat(self):
        return os.lstat(self)

    if hasattr(os, 'statvfs'):
        def statvfs(self):
            return os.statvfs(self)

    def chmod(self, mode):
        os.chmod(self, mode)

    if hasattr(os, 'chown'):
        def chown(self, uid, gid):
            os.chown(self, uid, gid)

    def set_times(self, mtime=None, atime=None):
        """Set a path's modification and access times.
           Times must be in ticks as returned by ``time.time()``.
           If 'mtime' is None, use the current time.
           If 'atime' is None, use 'mtime'.
           Creates an empty file if the path does not exists.
           On some platforms (Windows), the path must not be a directory.
        """
        if not self.exists():
            fd = os.open(self, os.O_WRONLY | os.O_CREAT, 0o666)
            os.close(fd)
        if mtime is None:
            mtime = time.time()
        if atime is None:
            atime = mtime
        times = atime, mtime
        os.utime(self, times)


    #### CREATING, REMOVING, AND RENAMING ####
    def mkdir(self, parents=False, mode=0o777):
        if self.exists():
            return
        if parents:
            os.makedirs(self, mode)
        else:
            os.mkdir(self, mode)

    def rmdir(self, parents=False):
        if not self.exists():
            return
        if parents:
            os.removedirs(self)
        else:
            os.rmdir(self)

    def remove(self):
        if self.lexists():
            os.remove(self)

    def rename(self, new, parents=False):
        if parents:
            os.renames(self, new)
        else:
            os.rename(self, new)

    #### SYMBOLIC AND HARD LINKS ####
    if hasattr(os, 'link'):
        def hardlink(self, newpath):
            """Create a hard link at 'newpath' pointing to self. """
            os.link(self, newpath)

    if hasattr(os, 'symlink'):
        def write_link(self, link_content):
            """Create a symbolic link at self pointing to 'link_content'.
               This is the same as .symlink but with the args reversed.
            """
            os.symlink(link_content, self)

        def make_relative_link_to(self, dest):
            """Make a relative symbolic link from self to dest.
            
            Same as self.write_link(self.rel_path_to(dest))
            """
            link_content = self.rel_path_to(dest)
            self.write_link(link_content)


    if hasattr(os, 'readlink'):
        def read_link(self, absolute=False):
            p = self.__class__(os.readlink(self))
            if absolute and not p.isabsolute():
                p = self.__class__(self.parent, p)
            return p

    #### HIGH-LEVEL OPERATIONS ####
    def copy(self, dst, times=False, perms=False):
        """Copy the file, optionally copying the permission bits (mode) and
           last access/modify time. If the destination file exists, it will be
           replaced. Raises OSError if the destination is a directory. If the
           platform does not have the ability to set the permission or times,
           ignore it.
           This is shutil.copyfile plus bits of shutil.copymode and
           shutil.copystat's implementation.
           shutil.copy and shutil.copy2 are not supported but are easy to do.
        """
        shutil.copyfile(self, dst)
        if times or perms:
            self.copy_stat(dst, times, perms)

    def copy_stat(self, dst, times=True, perms=True):
        st = os.stat(self)
        if hasattr(os, 'utime'):
            os.utime(dst, (st.st_atime, st.st_mtime))
        if hasattr(os, 'chmod'):
            m = stat.S_IMODE(st.st_mode)
            os.chmod(dst, m)

    # Undocumented, not implemented method.
    def copy_tree(dst, perserve_symlinks=False, times=False, perms=False):
        raise NotImplementedError()
        
    if hasattr(shutil, 'move'):
        move = shutil.move
        
    def needs_update(self, others):
        if not isinstance(others, (list, tuple)):
            others = [others]
        if not self.exists():
            return True
        control = self.mtime()
        for p in flatten(others):
            if p.isdir():
                for child in p.walk(filter=FILES):
                    if child.mtime() > control:
                        return True
            elif p.mtime() > control:
                return True
        return False
                
    def read_file(self, mode="rU"):
        f = open(self, mode)
        content = f.read()
        f.close()
        return content

    def rmtree(self, parents=False):
        """Delete self recursively, whether it's a file or directory.
           directory, remove it recursively (same as shutil.rmtree). If it
           doesn't exist, do nothing.
           If you're looking for a 'rmtree' method, this is what you want.
        """
        if self.isfile() or self.islink():
           os.remove(self)
        elif self.isdir():
           shutil.rmtree(self)
        if not parents:
            return
        p = self.parent
        while p:
            try:
                 os.rmdir(p)
            except os.error:
                break
            p = p.parent

    def write_file(self, content, mode="w"):
        f = open(self, mode)
        f.write(content)
        f.close()

