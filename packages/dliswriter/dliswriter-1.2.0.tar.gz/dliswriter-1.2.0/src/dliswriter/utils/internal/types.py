import os
import numpy as np
from typing import Union, TypeVar, TypedDict, Any
from datetime import datetime
import h5py  # type: ignore  # untyped library

from dliswriter.utils import enums


numpy_dtype_type = Union[np.dtype, type[np.generic]]

file_name_type = Union[str, os.PathLike[str]]
data_form_type = Union[dict[str, np.ndarray], file_name_type, np.ndarray]
data_source_type = Union[np.ndarray, dict[str, np.ndarray], h5py.File]

bytes_type = Union[bytes, bytearray]
number_type = Union[int, float]
dtime_or_number_type = Union[str, datetime, number_type]
list_of_values_type = Union[list[str], list[int], list[float]]

AttrDict = TypedDict('AttrDict', {'value': Any, 'units': Union[str, enums.Unit]}, total=False)

T = TypeVar('T')
ListOrTuple = Union[list[T], tuple[T, ...]]
NestedList = list[Union[T, 'NestedList[T]']]
