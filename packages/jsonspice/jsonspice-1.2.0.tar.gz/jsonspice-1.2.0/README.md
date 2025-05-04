<h1 align="center">
<img src="https://raw.githubusercontent.com/jacobwilliams/jsonspice/master/media/jsonspice.png" width=800">
</h1>

Python library to monkeypatch SpiceyPy to allow JSON kernels (and Python dictionaries).

[![CI Status](https://github.com/jacobwilliams/jsonspice/actions/workflows/CI.yml/badge.svg)](https://github.com/jacobwilliams/jsonspice/actions)
[![last-commit](https://img.shields.io/github/last-commit/jacobwilliams/jsonspice)](https://github.com/jacobwilliams/jsonspice/commits/master)
[![PyPI Downloads](https://img.shields.io/pypi/dm/jsonspice.svg?label=PyPI%20downloads)](https://pypi.org/project/jsonspice/)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/jsonspice.svg?label=Conda%20downloads)](https://anaconda.org/conda-forge/jsonspice)

### Description

The standard [text kernel format](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/pck.html) for the [SPICE Toolkit](https://naif.jpl.nasa.gov/naif/toolkit.html) is the "PCK" file (with extension `.tpc`). Examples of these files can be seen [here](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/).
The PCK file is a data file format that exists in no other domain. So, it may be more convenient to use a standard file format such as [JSON](https://www.json.org/json-en.html), as well as native Python dictionaries. The `jsonspice` library allows you to do this by [monkey patching](https://en.wikipedia.org/wiki/Monkey_patch#:~:text=In%20computer%20programming%2C%20monkey%20patching,altering%20the%20original%20source%20code.) [SpiceyPy](https://github.com/AndrewAnnex/SpiceyPy) so that JSON kernels will "just work".

### Installation

#### PyPi

```
pip install jsonspice
```

#### conda

```
conda install conda-forge::jsonspice
```

### JSON kernel format

The following PCK file:

```
KPL/PCK

\begintext
An example kernel

\begindata
TIME3      = @1972-JAN-1
AAA        = 1
AAA       += 2
VARIABLE   = (1.0 2.0 3.0)
VARIABLE2  = 42.0
```

Has the equivalent JSON kernel representation:

```json5
// An example kernel
{
    "TIME3": "@1972-JAN-1",
    "AAA" : 1,
    "+AAA" : 2,
    "VARIABLE": [1.0, 2.0, 3.0],
    "VARIABLE2": 42.0
}
```

Some things to note about the JSON version:

* Optional comments are supported (using the [JSON5](https://github.com/dpranke/pyjson5) library). Other than this, the file is a standard JSON file.
* The SPICE "@" format for time variables is supported using a normal string that begins with the "@" character.
* The SPICE "+=" assignment to append to an existing variable is supported by prepending the variable name with the "+" character.

The JSON version of SPICE "meta-kernels" is also supported. See the [SPICE documentation](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html) for details of that format.

### Example usage

To use this library, if must be imported BEFORE SpiceyPy. Once that is done, the normal `furnsh()` method can be used.

```python
import jsonspice  # import first to monkeypatch spiceypy
import spiceypy

# load a normal kernel
spiceypy.furnsh('de-403-masses.tpc')

# load a JSON kernel
spiceypy.furnsh('de-403-masses.json')

# also works with dicts:
spiceypy.furnsh({"BODY8_GM": 6836534.064})
spiceypy.furnsh({"time": '@1972-JAN-1'})
spiceypy.furnsh({"+abc": [4,5,6]})
```

### Documentation

The API documentation for the latest `master` branch can be found [here](https://jacobwilliams.github.io/jsonspice/).

### See also

* [NAIF](https://naif.jpl.nasa.gov/naif/) -- NASA's Navigation and Ancillary Information Facility
* [PCK Required Reading](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/pck.html) (NAIF)
* [SpiceyPy](https://github.com/AndrewAnnex/SpiceyPy) -- SpiceyPy: a Pythonic Wrapper for the SPICE Toolkit
* J. Williams, [JSON + SPICE](https://degenerateconic.com/json-spice.html), Feb 5, 2018 (degenerateconic.com)
* [jsonspice](https://pypi.org/project/jsonspice/) at the Python Package Index
* [jsonspice](https://anaconda.org/conda-forge/jsonspice) at conda-forge.
* [jsonspice-feedstock](https://github.com/conda-forge/jsonspice-feedstock) repo.
