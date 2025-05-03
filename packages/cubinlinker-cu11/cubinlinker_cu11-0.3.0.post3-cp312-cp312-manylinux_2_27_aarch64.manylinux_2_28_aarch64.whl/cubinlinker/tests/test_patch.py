# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.

import pytest
import sys
import os

from cubinlinker import patch, CubinLinkerError
from cubinlinker.patch import (
    PatchedLinker,
    _numba_version_ok,
    new_patched_linker,
    patch_numba_linker_if_needed,
    required_numba_ver,
)
from unittest.mock import patch as mock_patch


def test_numba_patching_numba_not_ok():
    with mock_patch.multiple(
            patch,
            _numba_version_ok=False,
            _numba_error='<error>'):
        with pytest.raises(RuntimeError, match='Cannot patch Numba: <error>'):
            patch_numba_linker_if_needed()


@pytest.mark.skipif(
    not _numba_version_ok,
    reason=f"Requires Numba == {required_numba_ver[0]}.{required_numba_ver[1]}"
)
def test_numba_patching():
    # We import the linker here rather than at the top level because the import
    # may fail if if Numba is not present or an unsupported version.
    from numba.cuda.cudadrv.driver import Linker

    # Force application of the patch so we can test application regardless of
    # whether it is needed.
    os.environ['PTXCOMPILER_APPLY_NUMBA_CODEGEN_PATCH'] = '1'

    patch_numba_linker_if_needed()
    assert Linker.new is new_patched_linker


def test_create():
    patched_linker = PatchedLinker(cc=(7, 5))
    assert "--gpu-name" in patched_linker.ptx_compile_options
    assert "sm_75" in patched_linker.ptx_compile_options
    assert "-c" in patched_linker.ptx_compile_options


def test_create_no_cc_error():
    # nvlink expects at least the architecture to be specified.
    with pytest.raises(RuntimeError,
                       match='PatchedLinker requires CC to be specified'):
        PatchedLinker()


def test_invalid_arch_error():
    # sm_XX is not a valid architecture
    with pytest.raises(CubinLinkerError,
                       match='NVLINK_ERROR_INVALID_ARCH error'):
        PatchedLinker(cc=(0, 0))


def test_invalid_cc_type_error():
    with pytest.raises(TypeError,
                       match='`cc` must be a list or tuple of length 2'):
        PatchedLinker(cc=0)


@pytest.mark.parametrize(
    "ptx_compile_options",
    [
        {"max_registers": None, "lineinfo": False},
        {"max_registers": 32, "lineinfo": False},
        {"max_registers": None, "lineinfo": True},
        {"max_registers": 32, "lineinfo": True},
    ]
)
def test_ptx_compile_options(ptx_compile_options):
    max_registers = ptx_compile_options["max_registers"]
    lineinfo = ptx_compile_options["lineinfo"]
    patched_linker = PatchedLinker(
        max_registers=max_registers,
        lineinfo=lineinfo,
        cc=(7, 5)
    )

    assert "--gpu-name" in patched_linker.ptx_compile_options
    assert "sm_75" in patched_linker.ptx_compile_options
    assert "-c" in patched_linker.ptx_compile_options

    if max_registers:
        assert (f"--maxrregcount={max_registers}"
                in patched_linker.ptx_compile_options)
    else:
        assert "--maxrregcount" not in patched_linker.ptx_compile_options

    if lineinfo:
        assert ("--generate-line-info"
                in patched_linker.ptx_compile_options)
    else:
        assert "--generate-line-info" not in patched_linker.ptx_compile_options


if __name__ == '__main__':
    sys.exit(pytest.main())
