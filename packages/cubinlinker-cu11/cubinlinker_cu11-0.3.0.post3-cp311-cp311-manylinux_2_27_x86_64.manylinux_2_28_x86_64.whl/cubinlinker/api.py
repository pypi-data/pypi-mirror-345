# Copyright (c) 2022, NVIDIA CORPORATION.

from cubinlinker import _nvlinklib

import weakref


class CubinLinkerError(RuntimeError):
    pass


class CubinLinker:
    def __init__(self, *options):
        try:
            self.handle = _nvlinklib.create(*options)
        except RuntimeError as e:
            raise CubinLinkerError(f"{e}")

        weakref.finalize(self, _nvlinklib.destroy, self.handle)

        self._info_log = None
        self._error_log = None

    @property
    def info_log(self):
        return self._info_log

    @property
    def error_log(self):
        return self._error_log

    def _add_data(self, fn, data, name):
        try:
            fn(self.handle, data, name)
        except RuntimeError as e:
            self._info_log = _nvlinklib.get_info_log(self.handle)
            self._error_log = _nvlinklib.get_error_log(self.handle)
            raise CubinLinkerError(f"{e}\n{self.error_log}")

    def add_cubin(self, cubin, name=None):
        name = name or 'unnamed-cubin'
        fn = _nvlinklib.add_cubin
        self._add_data(fn, cubin, name)

    def add_fatbin(self, fatbin, name=None):
        name = name or 'unnamed-fatbin'
        fn = _nvlinklib.add_fatbin
        self._add_data(fn, fatbin, name)

    def complete(self):
        try:
            _nvlinklib.finish(self.handle)
            return _nvlinklib.get_linked_cubin(self.handle)
        except RuntimeError as e:
            self._error_log = _nvlinklib.get_error_log(self.handle)
            raise CubinLinkerError(f"{e}\n{self.error_log}")
        finally:
            self._info_log = _nvlinklib.get_info_log(self.handle)
