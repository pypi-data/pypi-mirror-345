# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for handling deprecated functions.
The source code has originally been taken from the pyfakefs project.
See:
https://github.com/jmcgeheeiv/pyfakefs/blob/f5640e3ad4fc2a604f6d5fa00184bc13d715cb4d/pyfakefs/deprecator.py
"""  # noqa

import functools
import warnings


class Deprecated(object):
    """Decorator class for adding deprecated functions.
    Warnings are switched on by default.
    To disable deprecation warnings, use:
    >>> from microlib import Deprecated
    >>> Deprecated.show_warnings = False
    """

    show_warnings = True

    def __init__(self, use_instead=None, func_name=None, removal_version=None,
                 extra_msg=None, ref_url=None, removed=False):
        self.use_instead = use_instead
        self.func_name = func_name
        self.removal_version = removal_version
        self.extra_msg = extra_msg
        self.ref_url = ref_url
        self.removed = removed

    def __call__(self, func):
        """Decorator to mark functions as deprecated. Emit warning
        when the function is used."""

        @functools.wraps(func)
        def _new_func(*args, **kwargs):
            if self.show_warnings:
                with warnings.catch_warnings():
                    warnings.simplefilter('always', DeprecationWarning)
                    message = 'Call to deprecated function '\
                        f'{self.func_name or func.__name__}.'
                    if self.removed:
                        if self.removal_version:
                            message += ' It has been removed in '\
                                f'release {self.removal_version}.'
                        else:
                            message += ' It has been removed in a previous '\
                                'release.'
                    else:
                        if self.removal_version:
                            message += ' It will be removed in '\
                                f'release {self.removal_version}.'
                        else:
                            message += ' It might be removed in a future '\
                                'release.'
                    if self.use_instead:
                        message += f' Use {self.use_instead} instead.'
                    if self.extra_msg:
                        message += ' ' + self.extra_msg
                    if self.ref_url:
                        message += f' See {self.ref_url}'

                    warnings.warn(message, category=DeprecationWarning,
                                  stacklevel=2)
            return func(*args, **kwargs)

        return _new_func

    @staticmethod
    def add(clss, use_instead, deprecated_name, func_name=None,
            removal_version=None, extra_msg=None, ref_url=None, removed=True):
        """Add the deprecated version of a member function to the given class.
        Gives a deprecation warning on usage.
        Args:
            clss: the class where the deprecated function is to be added
            func: the actual function that is called by the deprecated version
            deprecated_name: the deprecated name of the function
        """

        @Deprecated(use_instead.__name__, func_name=deprecated_name,
                    removal_version=removal_version, extra_msg=extra_msg,
                    ref_url=ref_url, removed=removed)
        def _old_function(*args, **kwargs):
            return use_instead(*args, **kwargs)

        setattr(clss, deprecated_name, _old_function)
