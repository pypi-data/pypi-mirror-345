"""
.. include:: ../../README.md
"""

from .main import furnsh_json_kernel, furnsh_dict, _monkey_patch_spiceypy

_monkey_patch_spiceypy()  # Apply the monkey patch to spiceypy