import h5py    # type: ignore  # untyped library
import pytest
from pathlib import Path
import numpy as np

from tests.common import N_COLS, load_dlis, select_channel
from tests.dlis_files_for_testing import write_time_based_dlis, write_depth_based_dlis, write_dlis_from_dict


def test_dlis_depth_based(short_reference_data: h5py.File, short_reference_data_path: Path, new_dlis_path: Path)\
        -> None:
    """Create a depth-based DLIS file and check its basic parameters."""

    write_depth_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'depth'
        assert chan.units == 'm'
        assert chan.reprc == 7
        assert chan.origin == 1

        frame = f.frames[0]
        assert frame.index_type == 'DEPTH'
        assert frame.origin == 1

        index = short_reference_data['/contents/depth'][:]
        assert frame.index_min == index.min()
        assert frame.index_max == index.max()


def test_dlis_time_based(short_reference_data: h5py.File, short_reference_data_path: Path, new_dlis_path: Path) -> None:
    """Create a time-based DLIS file and check its basic parameters."""

    write_time_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'posix time'
        assert chan.units == 's'
        assert chan.reprc == 7
        assert chan.origin == 1

        frame = f.frames[0]
        assert frame.index_type == 'TIME'
        assert frame.origin == 1

        index = short_reference_data['/contents/time'][:]
        assert frame.index_min == index.min()
        assert frame.index_max == index.max()


def test_repr_code(short_reference_data_path: Path, new_dlis_path: Path) -> None:
    """Test that representation codes for the channels in DLIS are stored correctly."""

    write_time_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        assert select_channel(f, 'posix time').reprc == 7
        assert select_channel(f, 'surface rpm').reprc == 7
        assert select_channel(f, 'amplitude').reprc == 2
        assert select_channel(f, 'radius').reprc == 2
        assert select_channel(f, 'radius_pooh').reprc == 2


def test_channel_dimensions(short_reference_data_path: Path, new_dlis_path: Path) -> None:
    """Test that dimensions for the channels in DLIS are stored correctly."""

    write_time_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        def check(name: str, shape: list) -> None:
            ch = select_channel(f, name)
            assert ch.dimension == shape
            assert ch.element_limit == shape

        check('posix time', [1])
        check('surface rpm', [1])
        check('amplitude', [128])
        check('radius', [128])
        check('radius_pooh', [128])


@pytest.mark.parametrize('n_points', (10, 100, 128, 987))
def test_channel_curves(reference_data_path: Path, reference_data: h5py.File, new_dlis_path: Path,
                        n_points: int) -> None:
    """Create a DLIS file with varying number of points. Check that the data for each channel are correct."""

    write_time_based_dlis(new_dlis_path, data=reference_data_path, to_idx=n_points)

    with load_dlis(new_dlis_path) as f:
        for name in ('posix time', 'surface rpm'):
            curve = select_channel(f, name).curves()
            assert curve.shape == (n_points,)

        for name in ('amplitude', 'radius', 'radius_pooh'):
            curve = select_channel(f, name).curves()
            assert curve.shape == (n_points, N_COLS)

        def check_contents(channel_name: str, data_name: str) -> None:
            curve = select_channel(f, channel_name).curves()
            data = reference_data[data_name][:n_points]
            assert pytest.approx(curve) == data

        check_contents('posix time', '/contents/time')
        check_contents('surface rpm', '/contents/rpm')
        check_contents('amplitude', '/contents/image0')
        check_contents('radius', '/contents/image1')
        check_contents('radius_pooh', '/contents/image2')


@pytest.mark.parametrize('data_arr', (
    np.random.rand(100).astype(np.float64),
    np.random.rand(30, 10).astype(np.float32),
    np.random.randint(0, 2**32, size=(2, 30), dtype=np.uint32),
    np.random.randint(0, 2**16, size=(100, 5), dtype=np.uint16),
    np.random.randint(0, 2**8, size=15, dtype=np.uint8),
    np.random.randint(-2**16, 2**16, size=280, dtype=np.int32),
    np.random.randint(-2**15, 2**15, size=33, dtype=np.int16),
    np.random.randint(-2**7, 2**7, size=(12, 13), dtype=np.int8)
))
def test_all_numpy_dtypes(new_dlis_path: Path, data_arr: np.ndarray) -> None:

    data_arr = np.atleast_2d(data_arr)
    data_dict = {
        'index': np.arange(data_arr.shape[0]).astype(np.float64),
        'data': data_arr
    }

    write_dlis_from_dict(new_dlis_path, data_dict=data_dict)

    with load_dlis(new_dlis_path) as f:
        ch = select_channel(f, 'data')
        assert ch.dimension == [data_arr.shape[-1]]
        assert ch.curves().dtype == data_arr.dtype
        assert (ch.curves() == data_arr).all()


@pytest.mark.parametrize(('data_arr', 'cast_dtype', 'rc'), (
    (np.random.randint(-10, 30, (10, 3)), np.float64, 7),
    (np.random.rand(30, 10) + 20, np.float32, 2),
    (np.random.randint(0, 2**16, size=(2, 30), dtype=np.uint16), np.uint32, 17),
    (1024 * np.random.rand(100), np.uint16, 16),
    (30 * np.random.rand(128, 10), np.uint8, 15),
    (np.random.randint(-2**16, 2**16, size=100), np.int32, 14),
    (100 * np.random.rand(20) - 30, np.int16, 13),
    (50 * np.random.rand(12, 13) - 40, np.int8, 12)
))
def test_numpy_dtypes_with_casting(new_dlis_path: Path, data_arr: np.ndarray, cast_dtype: type[np.generic],
                                   rc: int) -> None:

    data_arr = np.atleast_2d(data_arr)
    data_dict = {
        'index': np.arange(data_arr.shape[0]).astype(np.float64),
        'data': data_arr
    }

    write_dlis_from_dict(new_dlis_path, data_dict=data_dict, channel_kwargs={'data': {'cast_dtype': cast_dtype}})

    with load_dlis(new_dlis_path) as f:
        ch = select_channel(f, 'data')
        assert ch.dimension == [data_arr.shape[-1]]
        assert ch.reprc == rc
        assert ch.curves().dtype == cast_dtype
        assert (ch.curves() == data_arr.astype(cast_dtype)).all()
