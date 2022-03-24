# Copyright (C) 2022 Patrick Ziegler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class StatementScanner:

    _filt = {}
    _conv = {}
    _conv_update = {}

    @classmethod
    def register_filt(cls, key):
        def wrap(fn):
            cls._filt[key] = fn
        return wrap

    @classmethod
    def register_conv(cls, key):
        def wrap(fn):
            cls._conv[key] = fn
        return wrap

    @classmethod
    def register_conv_update(cls, key):
        def wrap(fn):
            cls._conv_update[key] = fn
        return wrap

    def __init__(self, key):
        self.key = key

    def filt(self, *args, **kwargs):
        return self._filt[self.key](*args, **kwargs)

    def conv(self, *args, **kwargs):
        return self._conv[self.key](*args, **kwargs)

    def conv_update(self, *args, **kwargs):
        return self._conv_update[self.key](*args, **kwargs)
