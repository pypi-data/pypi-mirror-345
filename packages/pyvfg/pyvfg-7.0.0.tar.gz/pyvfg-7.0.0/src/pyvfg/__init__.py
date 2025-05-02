# -*- coding: utf-8 -*-

from .errors import *
from .versions.vfg_0_5_0 import *
from .versions.vfg_0_5_0_utils import (
    vfg_from_dict,
    vfg_from_json,
    vfg_to_json,
    vfg_to_json_schema,
    vfg_upgrade,
)


# by request
@property
def __version__() -> str:
    import importlib_metadata

    return importlib_metadata.version("pyvfg")


# for compatibility
VFGPydanticType = VFG
validate_graph = VFG.validate
