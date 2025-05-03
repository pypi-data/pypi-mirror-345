# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.

import pytest
import sys
import os

from cubinlinker import _nvlinklib


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
    with pytest.raises(RuntimeError,
                       match='NVLINK_ERROR_INVALID_ARCH error'):
        _nvlinklib.create()


def test_invalid_arch_error():
    # sm_XX is not a valid architecture
    with pytest.raises(RuntimeError,
                       match='NVLINK_ERROR_INVALID_ARCH error'):
        _nvlinklib.create('-arch', 'sm_XX')


def test_invalid_option_type_error():
    with pytest.raises(TypeError,
                       match='Expecting only strings'):
        _nvlinklib.create('-arch', 53)


def test_create_and_destroy():
    handle = _nvlinklib.create('-arch=sm_53')
    assert handle != 0
    _nvlinklib.destroy(handle)


def test_multiple_args_arch():
    handle = _nvlinklib.create('-arch', 'sm_53')
    assert handle != 0
    _nvlinklib.destroy(handle)


def test_add_cubin(device_functions_cubin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    _nvlinklib.destroy(handle)


def test_add_incompatible_cubin_arch_error(device_functions_cubin):
    handle = _nvlinklib.create('-arch', 'sm_70')
    name = 'test_device_functions.cubin'
    with pytest.raises(RuntimeError,
                       match='NVLINK_ERROR_INCOMPATIBLE error'):
        _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    _nvlinklib.destroy(handle)


def test_add_fatbin_sm75(device_functions_fatbin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.fatbin'
    _nvlinklib.add_fatbin(handle, device_functions_fatbin, name)
    _nvlinklib.destroy(handle)


def test_add_fatbin_sm70(device_functions_fatbin):
    handle = _nvlinklib.create('-arch', 'sm_70')
    name = 'test_device_functions.fatbin'
    _nvlinklib.add_fatbin(handle, device_functions_fatbin, name)
    _nvlinklib.destroy(handle)


def test_add_incompatible_fatbin_arch_error(device_functions_fatbin):
    handle = _nvlinklib.create('-arch', 'sm_80')
    name = 'test_device_functions.fatbin'
    with pytest.raises(RuntimeError,
                       match='NVLINK_ERROR_INVALID_INPUT error'):
        _nvlinklib.add_fatbin(handle, device_functions_fatbin, name)
    _nvlinklib.destroy(handle)


def test_add_cubin_with_fatbin_error(device_functions_fatbin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.fatbin'
    with pytest.raises(RuntimeError,
                       match='NVLINK_ERROR_INVALID_CUBIN error'):
        _nvlinklib.add_cubin(handle, device_functions_fatbin, name)
    _nvlinklib.destroy(handle)


def test_add_fatbin_with_cubin(device_functions_cubin):
    # Adding a cubin with add_fatbin seems to work - this may be expected
    # behaviour.
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_fatbin(handle, device_functions_cubin, name)
    _nvlinklib.destroy(handle)


def test_duplicate_symbols_cubin_and_fatbin(device_functions_cubin,
                                            device_functions_fatbin):
    # This link errors because the cubin and the fatbin contain the same
    # symbols.
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    name = 'test_device_functions.fatbin'
    with pytest.raises(RuntimeError,
                       match="NVLINK_ERROR_LINK error"):
        _nvlinklib.add_fatbin(handle, device_functions_fatbin, name)
    _nvlinklib.destroy(handle)


def test_finish_cubin(device_functions_cubin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    _nvlinklib.finish(handle)
    _nvlinklib.destroy(handle)


def test_finish_fatbin(device_functions_fatbin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.fatbin'
    _nvlinklib.add_fatbin(handle, device_functions_fatbin, name)
    _nvlinklib.finish(handle)
    _nvlinklib.destroy(handle)


def test_finish_empty_error():
    handle = _nvlinklib.create('-arch', 'sm_75')
    with pytest.raises(RuntimeError,
                       match="NVLINK_ERROR_NO_CUBIN error"):
        _nvlinklib.finish(handle)
    _nvlinklib.destroy(handle)


def test_get_linked_cubin(device_functions_cubin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    _nvlinklib.finish(handle)
    cubin = _nvlinklib.get_linked_cubin(handle)
    _nvlinklib.destroy(handle)

    # Just check we got something that looks like an ELF
    assert cubin[:4] == b'\x7fELF'


def test_get_linked_cubin_link_not_finished_error(device_functions_cubin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    with pytest.raises(RuntimeError,
                       match="NVLINK_ERROR_LINK_FINISH_INCOMPLETE error"):
        _nvlinklib.get_linked_cubin(handle)
    _nvlinklib.destroy(handle)


def test_get_error_log(undefined_extern_cubin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'undefined_extern.cubin'
    _nvlinklib.add_cubin(handle, undefined_extern_cubin, name)
    with pytest.raises(RuntimeError):
        _nvlinklib.finish(handle)
    error_log = _nvlinklib.get_error_log(handle)
    _nvlinklib.destroy(handle)
    assert "Undefined reference to '_Z5undefff'" in error_log


def test_get_info_log(device_functions_cubin):
    handle = _nvlinklib.create('-arch', 'sm_75')
    name = 'test_device_functions.cubin'
    _nvlinklib.add_cubin(handle, device_functions_cubin, name)
    _nvlinklib.finish(handle)
    info_log = _nvlinklib.get_info_log(handle)
    _nvlinklib.destroy(handle)
    # Info log is empty
    assert "" == info_log


if __name__ == '__main__':
    sys.exit(pytest.main())
