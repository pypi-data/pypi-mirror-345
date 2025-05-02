import json

from pyvfg import vfg_upgrade
from .. import package_dir


def test_vfg_020_from_json():
    file_path = (
        package_dir / "tests/fixtures/models" / "sprinkler/sprinkler_vfg_0_2_0.json"
    )
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vfg = vfg_upgrade(data)

    assert vfg.version == "0.4.0"
    for factor, factor_data in zip(vfg.factors, data["factors"]):
        assert factor.variables == factor_data["variables"]
        # assert factor.values == factor_data["values"]
