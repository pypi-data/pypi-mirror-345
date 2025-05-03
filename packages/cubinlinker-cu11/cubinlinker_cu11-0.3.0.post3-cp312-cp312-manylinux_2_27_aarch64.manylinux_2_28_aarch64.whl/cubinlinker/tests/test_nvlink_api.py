# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.

import pytest
import sys
import os

from cubinlinker import CubinLinker, CubinLinkerError


@pytest.fixture
def device_functions_cubin():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    cubin_path = os.path.join(test_dir, 'test_device_functions.cubin')
    with open(cubin_path, 'rb') as f:
        return f.read()


@pytest.fixture
def device_functions_fatbin():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    fatbin_path = os.path.join(test_dir, 'test_device_functions.fatbin')
    with open(fatbin_path, 'rb') as f:
        return f.read()


@pytest.fixture
def undefined_extern_cubin():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    fatbin_path = os.path.join(test_dir, 'undefined_extern.cubin')
    with open(fatbin_path, 'rb') as f:
        return f.read()


def test_create_no_arch_error():
    # nvlink expects at least the architecture to be specified.
    with pytest.raises(CubinLinkerError,
                       match='NVLINK_ERROR_INVALID_ARCH error'):
        CubinLinker()


def test_invalid_arch_error():
    # sm_XX is not a valid architecture
    with pytest.raises(CubinLinkerError,
                       match='NVLINK_ERROR_INVALID_ARCH error'):
        CubinLinker('-arch', 'sm_XX')


def test_invalid_option_type_error():
    with pytest.raises(TypeError,
                       match='Expecting only strings'):
        CubinLinker('-arch', 53)


def test_create_and_destroy():
    cubin_linker = CubinLinker('-arch=sm_53')
    assert cubin_linker.handle != 0


def test_multiple_args_arch():
    cubin_linker = CubinLinker('-arch', 'sm_53')
    assert cubin_linker.handle != 0


def test_add_cubin(device_functions_cubin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    cubin_linker.add_cubin(device_functions_cubin, name)


def test_add_incompatible_cubin_arch_error(device_functions_cubin):
    cubin_linker = CubinLinker('-arch', 'sm_70')
    name = 'test_device_functions.cubin'
    with pytest.raises(CubinLinkerError,
                       match='NVLINK_ERROR_INCOMPATIBLE error'):
        cubin_linker.add_cubin(device_functions_cubin, name)


def test_add_fatbin_sm75(device_functions_fatbin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.fatbin'
    cubin_linker.add_fatbin(device_functions_fatbin, name)


def test_add_fatbin_sm70(device_functions_fatbin):
    cubin_linker = CubinLinker('-arch', 'sm_70')
    name = 'test_device_functions.fatbin'
    cubin_linker.add_fatbin(device_functions_fatbin, name)


def test_add_incompatible_fatbin_arch_error(device_functions_fatbin):
    cubin_linker = CubinLinker('-arch', 'sm_80')
    name = 'test_device_functions.fatbin'
    with pytest.raises(CubinLinkerError,
                       match='NVLINK_ERROR_INVALID_INPUT error'):
        cubin_linker.add_fatbin(device_functions_fatbin, name)


def test_add_cubin_with_fatbin_error(device_functions_fatbin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.fatbin'
    with pytest.raises(CubinLinkerError,
                       match='NVLINK_ERROR_INVALID_CUBIN error'):
        cubin_linker.add_cubin(device_functions_fatbin, name)


def test_add_fatbin_with_cubin(device_functions_cubin):
    # Adding a cubin with add_fatbin seems to work - this may be expected
    # behaviour.
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    cubin_linker.add_fatbin(device_functions_cubin, name)


def test_duplicate_symbols_cubin_and_fatbin(device_functions_cubin,
                                            device_functions_fatbin):
    # This link errors because the cubin and the fatbin contain the same
    # symbols.
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    cubin_linker.add_cubin(device_functions_cubin, name)
    name = 'test_device_functions.fatbin'
    with pytest.raises(CubinLinkerError,
                       match="NVLINK_ERROR_LINK error"):
        cubin_linker.add_fatbin(device_functions_fatbin, name)


def test_complete_cubin(device_functions_cubin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    cubin_linker.add_cubin(device_functions_cubin, name)
    cubin_linker.complete()


def test_complete_fatbin(device_functions_fatbin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.fatbin'
    cubin_linker.add_fatbin(device_functions_fatbin, name)
    cubin_linker.complete()


def test_complete_empty_error():
    cubin_linker = CubinLinker('-arch', 'sm_75')
    with pytest.raises(CubinLinkerError,
                       match="NVLINK_ERROR_NO_CUBIN error"):
        cubin_linker.complete()


def test_get_linked_cubin(device_functions_cubin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    cubin_linker.add_cubin(device_functions_cubin, name)
    cubin = cubin_linker.complete()

    # Just check we got something that looks like an ELF
    assert cubin[:4] == b'\x7fELF'


def test_get_error_log(undefined_extern_cubin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'undefined_extern.cubin'
    cubin_linker.add_cubin(undefined_extern_cubin, name)
    with pytest.raises(CubinLinkerError):
        cubin_linker.complete()
    error_log = cubin_linker.error_log
    assert "Undefined reference to '_Z5undefff'" in error_log


def test_get_info_log(device_functions_cubin):
    cubin_linker = CubinLinker('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    cubin_linker.add_cubin(device_functions_cubin, name)
    cubin_linker.complete()
    info_log = cubin_linker.info_log
    # Info log is empty
    assert "" == info_log


if __name__ == '__main__':
    sys.exit(pytest.main())
