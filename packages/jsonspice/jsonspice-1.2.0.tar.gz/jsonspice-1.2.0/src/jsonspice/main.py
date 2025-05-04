"""
Main module for loading JSON kernels into SPICE using spiceypy.
"""

import spiceypy
from spiceypy import tparse, pdpool, pcpool, dtpool, gcpool, gdpool, dvpool
from typing import Iterable, Union
from pathlib import Path
try:
    # this will allow loading JSON files with comments
    import json5 as json
except ImportError:
    # if not present, fallback to regular json (won't allow comments)
    import json

class _spiceypy_cache:
    """Just to cache the original `spiceypy.spiceypy.furnsh` function"""
    furnsh = spiceypy.spiceypy.furnsh

def _monkey_patch_spiceypy():
    """
    Monkey patch the `furnsh` function in spiceypy to support JSON kernels.
    """
    spiceypy.spiceypy.furnsh = furnsh_json_kernel
    spiceypy.furnsh = furnsh_json_kernel

def furnsh_json_kernel(kernel_path: Union[str, Path, dict, Iterable[str]]) -> None:
    """
    Load a JSON kernel into SPICE.
    When jsonspice is imported, this function replaces the
    `spiceypy.furnsh` function to support JSON kernels.

    See: `furnsh_dict` for details.

    Args:
        kernel_path (str | Path | list of strings | dict)
            The path(s) to the JSON kernel file(s) or a dictionary containing the kernel data.
    """

    if isinstance(kernel_path, dict):
        # if a dictionary is passed, use it directly
        furnsh_dict(kernel_path)
    elif spiceypy.stypes.is_iterable(kernel_path):
        # if an iterable is passed, assume it is a list of paths
        for p in kernel_path:
            furnsh_json_kernel(p)
    elif isinstance(kernel_path, (Path, str)):
        if (isinstance(kernel_path, Path)):
            kernel_path = str(kernel_path.resolve())
        if not kernel_path.lower().endswith('.json'):
            # in this case, just use a normal furnsh
            _spiceypy_cache.furnsh(kernel_path)
        else:
            # use the custom routine:
            with open(kernel_path, 'r') as f:
                data = json.load(f)
            furnsh_dict(data)
    else:
        raise TypeError("kernel_path must be a string or a dictionary.")

def furnsh_dict(data: dict) -> None:
    """
    Load a JSON kernel data into SPICE.

    Note: there are two modifications to support JSON SPICE kernels:

    1. if the variable name starts with '+', then the SPICE '+=' syntax
       is used to add to an existing variable if it exists.
    2. if a string value starts with '@', it is treated as a UTC string
       and converted to a double precision number representing "UTC seconds past J2000".

    Reference: https://degenerateconic.com/json-spice.html

    Args:
        d (dict) The JSON kernel data as a dictionary.
    """

    # first account for meta-kernel variables in this file.
    # they must all the strings.
    # path_values and path_symbols must be the same length.
    # the variables themselves are not added to the pool.
    path_values     = _get_string_array('PATH_VALUES', data)
    path_symbols    = _get_string_array('PATH_SYMBOLS', data)
    kernels_to_load = _get_string_array('KERNELS_TO_LOAD', data)
    if len(path_values) != len(path_symbols):
        # SPICE(PATHMISMATCH)
        raise Exception(f"Number of path symbols is {len(path_symbols)}; number of path values is {len(path_values)}; counts must match.")
    if kernels_to_load:
        for path, symbol in zip(path_values, path_symbols):
            # replace the symbol with the path value
            kernels_to_load = [k.replace(f'${symbol}', path) for k in kernels_to_load]
        furnsh_json_kernel(kernels_to_load)

    # now process the rest of the variables:
    for item, value in data.items():

        if isinstance(value, (list, tuple)):  # a list of values
            n = len(value)
            if n == 0:
                raise Exception("Empty arrays are not supported in JSON SPICE kernels.")

            # first if any are strings, check for @ syntax and convert to int
            value = [_tparse_wrapper(x) for x in value]  # apply tparse to all elements

            # what is the type of this list?
            if all(isinstance(x, str) for x in value):
                # a list of strings
                t = str
            elif all(isinstance(x, (int, bool, float)) for x in value):
                # a list of integers, floats, bools
                t = float
                value = [float(x) for x in value]
            else:
                raise Exception("Unsupported array type in JSON SPICE kernel.")

        elif isinstance(value, str):
            n = 1
            value = _tparse_wrapper(value)
            t = type(value)
            value = [value]

        elif isinstance(value, (int, float, bool)):
            n = 1
            t = float
            value = [float(value)]

        elif isinstance(value, dict):
            raise Exception("Nested dictionaries are not supported in JSON SPICE kernels.")

        # check for += and add to existing variable if it exists
        if item.startswith('+'):

            item = item[1:]
            try:
                n_existing, typeout = dtpool(item)
                found = n_existing > 0 and typeout != 'X'
            except:
                found = False

            if found:
                if typeout == 'C':  # character
                    if t == str:
                        values = [str(s) for s in gcpool(item, 0, n)]
                    else:
                        raise Exception("Cannot add to existing character variable with a non-string value.")
                elif typeout == 'N':  # numeric
                    if t == float:
                        values = [float(x) for x in gdpool(item, 0, n)]
                    else:
                        raise Exception("Cannot add to existing numeric variable with a non-float value.")
                if found:
                    values.extend(value)  # append new values to existing ones
                    value = values
                    dvpool(item)  # delete the existing variable from the pool
                else:
                    raise Exception(f"Variable '{item}' not found in SPICE pool for += operation.")

        # add the variable
        if t == float:
            pdpool ( item, value )
        elif t == str:
            pcpool ( item, value )

def _tparse_wrapper(x):
    """wrapper for `tparse` to either return the result or the original string if parsing fails."""
    if isinstance(x, str) and x.startswith('@'):
        # convert to UTC seconds past J2000
        val, msg = tparse(x[1:])
        if msg:
            return x  # as is
        else:
            return val
    else:
        return x

def _get_string_array(name: str, data: dict) -> list:
    """
    If data[name] is a string or list of strings, then
    return it as a list of strings. Otherwise, return an empty list.
    Remove it from the dict if present.

    Note that the + syntax is not supported for these.
    (does SPICE support that?)
    """
    val = data.pop(name, None) or []
    if val:
        if not isinstance(val, (list, tuple)):
            val = [val]
        if all(isinstance(x, str) for x in val):
            return val
    return []
