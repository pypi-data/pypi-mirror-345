import json
import pathlib

import pytest
from pyvfg import vfg_upgrade

package_dir = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "gpil"


@pytest.mark.parametrize(
    "full_path",
    [
        "tests/fixtures/vfg/vfg_0_4_0_sample.json",
        "tests/fixtures/models/insurance/insurance_vfg_0_3_0.json",
        "tests/fixtures/models/sprinkler/sprinkler_vfg_0_3_0.json",
        "tests/fixtures/models/gridworld/gridworld_vfg_v0_3_0.json",
        "tests/fixtures/models/multi_armed_bandit/mab_vfg_v0_3_0.json",
        "tests/fixtures/models/insurance/insurance_vfg_0_4_0.json",
        "tests/fixtures/models/calendar_assistant/calendar_assistant_vfg_0_4_0.json",
    ],
)
def test_vfg_040_from_json(full_path):
    file_path = package_dir / full_path
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vfg = vfg_upgrade(data)

    assert vfg.version == "0.5.0"
    for factor, factor_data in zip(vfg.factors, data["factors"]):
        assert factor.variables == factor_data["variables"]
