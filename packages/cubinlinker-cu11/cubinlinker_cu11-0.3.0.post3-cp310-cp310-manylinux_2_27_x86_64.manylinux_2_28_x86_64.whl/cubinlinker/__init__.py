# Copyright (c) 2022, NVIDIA CORPORATION.

from cubinlinker.api import CubinLinker, CubinLinkerError

__all__ = (CubinLinker, CubinLinkerError)

from . import _version
__version__ = _version.get_versions()['version']
