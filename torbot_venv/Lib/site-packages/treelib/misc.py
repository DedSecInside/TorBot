#!/usr/bin/env python
# Copyright (C) 2011
# Brett Alistair Kromkamp - brettkromkamp@gmail.com
# Copyright (C) 2012-2017
# Xiaming Chen - chenxm35@gmail.com
# and other contributors.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
from warnings import warn, simplefilter


def deprecated(alias):
    def real_deco(func):
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emmitted
        when the function is used.
        Derived from answer by Leando: https://stackoverflow.com/a/30253848
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            simplefilter('always', DeprecationWarning)  # turn off filter
            warn('Call to deprecated function "{}"; use "{}" instead.'.format(func.__name__, alias),
                 category=DeprecationWarning, stacklevel=2)
            simplefilter('default', DeprecationWarning)  # reset filter
            return func(*args, **kwargs)

        return wrapper

    return real_deco
