"""
Create a Numpy array from an array descriptor of a C-array
"""

import numpy as np
import ctypes

class Arrayf64Converter:
    """
    Module to convert a C-Array of type double to a Numpy array.
    """

    # C-types
    dim_t = ctypes.c_size_t  # type of dimensions
    value_t = ctypes.c_double  # type of the array elements

    @staticmethod
    def _pyArrayPtr(a_ptr:'C pointer', dtype, asize:int):
        """
        Returns a ctypes pointer which wraps a given raw C-pointer.
        """
        py_arr_ptr = (dtype * asize).from_address(int(a_ptr))
        return py_arr_ptr

    @staticmethod
    def _npArrayFromPyPtr(py_arr_ptr:'ctypes pointer', dims:list):
        """
        Returns a Numpy array which wraps a ctypes pointer.
        Array data are _not_ copied.
        """
        np_array = np.ctypeslib.as_array(py_arr_ptr).reshape(dims)
        return np_array

    @staticmethod
    def asNpArray(array_desc:'Arrayf64Wrapper'):
        """
        Returns a Numpy array which wraps a C-array of type double.
        Array data are _not_ copied.
        """

        # extract the descriptors for the C-array
        asize = array_desc.size()
        n_dims = array_desc.n_dimensions()
        dims_ptr = array_desc.dimensions()
        array_ptr = array_desc.arrayPtr()

        # verify the array
        if asize < 1 or n_dims < 1 or not dims_ptr or not array_ptr:
            return None

        # convert the array dimensions into a Python tuple
        py_dims_ptr = __class__._pyArrayPtr(dims_ptr, __class__.dim_t, n_dims)
        py_dims = tuple(py_dims_ptr)

        # create a Numpy array to wrap the C-array pointer
        py_array_ptr = __class__._pyArrayPtr(array_ptr, __class__.value_t, asize)
        np_array_wrapper = __class__._npArrayFromPyPtr(py_array_ptr, py_dims)

        return np_array_wrapper

    @staticmethod
    def npArray(array_desc:'Arrayf64Wrapper'):
        """
        Returns a Numpy array from a C-array of type double.
        Array data are copied.
        """

        np_array_wrapper = __class__.asNpArray(array_desc)

        if np_array_wrapper is None:
            return None

        np_array = np.copy(np_array_wrapper)
        return np_array
