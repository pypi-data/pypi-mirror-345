import pathlib
import os
import pytest
import json
from pyvfg import vfg_from_json
from pyvfg.versions.vfg_0_5_0 import VFG

package_dir = pathlib.Path(__file__).resolve().parent.parent


#######################################################
## VFG 0_4_0
#######################################################
def get_json(full_path) -> dict:
    file_path = package_dir / full_path
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_vfg(full_path) -> VFG:
    vfg_json = get_json(full_path)
    return vfg_from_json(vfg_json)


@pytest.fixture
def variables_1():
    return {
        "var_elements": {
            "elements": ["a", "b", "c"],
            "role": "control_state",
        },
        "var_cardinality": {
            "cardinality": 3,
            "role": "latent",
        },
    }


@pytest.fixture
def factors_1():
    return [
        {
            "variables": ["var_elements", "var_cardinality"],
            "distribution": "categorical",
            "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            "role": "transition",
        }
    ]


@pytest.fixture
def metadata_1():
    return {
        "model_type": "markov_random_field",
        "model_version": "0.5.0",
    }


@pytest.fixture
def vis_1():
    return {
        "class": "name",
        "style": "lame",
    }


# TODO: These two are duplicated from gpil/tests/conftest.py. Can we import that instead?
@pytest.fixture
def mab_vfg() -> VFG:
    full_path = os.path.join(
        package_dir.parent.parent,
        "gpil/tests/fixtures/models/multi_armed_bandit/mab_vfg_v0_3_0.json",
    )
    return get_vfg(full_path)


@pytest.fixture
def sprinkler_vfg() -> VFG:
    full_path = os.path.join(
        package_dir.parent.parent,
        "gpil/tests/fixtures/models/sprinkler/sprinkler_vfg_0_3_0.json",
    )
    return get_vfg(full_path)
