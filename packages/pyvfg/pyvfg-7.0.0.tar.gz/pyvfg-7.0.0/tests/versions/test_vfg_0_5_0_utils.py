import json
import pathlib

import pytest
from pyvfg import vfg_to_json_schema, vfg_upgrade
from pyvfg.errors import JsonSerializationError
from pyvfg.versions.vfg_0_5_0 import (
    VFG,
    DiscreteVariableAnonymousElements,
    DiscreteVariableNamedElements,
    Distribution,
    Factor,
    ValidationErrors,
    Variable,
)

package_dir = pathlib.Path(__file__).resolve().parents[2]


def test_vfg_to_dict_default():
    vfg = VFG()
    vfg_dict = vfg.to_dict()
    assert vfg_dict["variables"] == {}
    assert vfg_dict["factors"] == []


def test_vfg_to_dict_custom(variables_1, factors_1, metadata_1, vis_1):
    vfg = VFG(variables=variables_1, factors=factors_1)
    vfg.metadata = metadata_1
    vfg.visualization_metadata = vis_1
    vfg_dict = vfg.to_dict()

    assert vfg_dict["variables"] == variables_1
    assert vfg_dict["factors"][0]["variables"] == factors_1[0]["variables"]
    assert vfg_dict["factors"][0]["distribution"] == factors_1[0]["distribution"]
    assert vfg_dict["factors"][0]["values"] == factors_1[0]["values"]
    assert vfg_dict["factors"][0]["role"] == factors_1[0]["role"]
    assert vfg_dict["metadata"] == metadata_1
    assert vfg_dict["visualization_metadata"] == vis_1


def test_vfg_to_json_schema():
    vfg_schema_dict, _ = vfg_to_json_schema()

    assert vfg_schema_dict["title"] == "VFG"
    assert vfg_schema_dict["type"] == "object"
    assert vfg_schema_dict["properties"]["variables"]["type"] == "object"
    assert vfg_schema_dict["properties"]["version"]["default"] == "0.5.0"
    assert vfg_schema_dict["properties"]["factors"]["type"] == "array"


def test_factor_to_json_schema():
    factor_schema_dict = Factor.model_json_schema()

    assert factor_schema_dict["title"] == "Factor"
    assert factor_schema_dict["type"] == "object"
    assert factor_schema_dict["properties"]["variables"]["type"] == "array"
    assert factor_schema_dict["properties"]["values"]["$ref"] == "#/$defs/Tensor"


def test_generated_vfg_schema(mab_vfg: VFG):
    vfg_schema_dict, _ = vfg_to_json_schema()

    import jsonschema

    jsonschema.validate(
        schema=vfg_schema_dict, instance=json.loads(mab_vfg.model_dump_json())
    )
    assert True, "Generated schema is valid"


# Valid VFG examples
@pytest.fixture
def valid_vfg_1():
    with open(
        package_dir
        / "../gpil/tests/fixtures/models/sprinkler/sprinkler_vfg_0_3_0.json",
        "r",
    ) as f:
        vfg_json = json.load(f)
    return VFG(**vfg_json)


@pytest.fixture
def valid_vfg_2():
    with open(
        package_dir
        / "../gpil/tests/fixtures/models/insurance/insurance_vfg_0_5_0.json",
        "r",
    ) as f:
        vfg_json = json.load(f)
    return VFG(**vfg_json)


# Invalid VFG examples
@pytest.fixture
def invalid_vfg_1():
    variables = {
        "x?": Variable(DiscreteVariableNamedElements(elements=["a", "b", "c"])),
        "y": Variable(DiscreteVariableAnonymousElements(cardinality=2)),
    }
    factors = [
        Factor(
            variables=["x?", "y"],
            distribution=Distribution.Categorical,
            values=[0.1, 0.2, 0.3],
        )
    ]
    return VFG(variables=variables, factors=factors)


@pytest.fixture
def invalid_vfg_2():
    variables = {
        "a": Variable(DiscreteVariableNamedElements(elements=["x", "y", "z"])),
        "b": Variable(DiscreteVariableAnonymousElements(cardinality=2)),
    }
    factors = [
        Factor(
            variables=["a", "b"],
            distribution=Distribution.Categorical,
            values=[0.1, 0.2, 0.3],
        )
    ]
    return VFG(variables=variables, factors=factors)


def test_validate_valid_vfg(valid_vfg_1: VFG, valid_vfg_2: VFG):
    assert not valid_vfg_1.validate(), "VFG should be valid"
    assert not valid_vfg_2.validate(), "VFG should be valid"


def test_validate_invalid_vfg(invalid_vfg_1: VFG, invalid_vfg_2: VFG):
    # TODO: Restore once variable name check is settled
    # try:
    #     invalid_vfg_1.validate()
    #     assert False, "should not reach here"
    # except InvalidVariableName as e:
    #     assert "x?" in str(e)

    try:
        invalid_vfg_2.validate()
        assert False, "should not reach here"
    except ValidationErrors as e:
        assert (
            "Factor 0 's tensor shape [3] is incompatible with its variable cardinalities [3, 2]."
            in str(e.errors[0])
        )


def test_vfg_upgrade(valid_vfg_2: VFG):
    vfg = vfg_upgrade(valid_vfg_2.model_dump())
    assert not vfg.validate(), "check for validity"
    assert vfg == valid_vfg_2, "check for round trip"
    vfg = vfg_upgrade(valid_vfg_2.model_dump_json())
    assert not vfg.validate(), "check for string validity"
    assert vfg == valid_vfg_2, "check for string round-trip"


@pytest.mark.parametrize(
    "f",
    [
        "post_validate_empty_values_array.json",
        "post_validate_missing_required_fields_factors.json",
    ],
)
def test_validate_graph_failure(f):
    """
    Tests graph validation, with the same procedure as gpil-pipeline.
    :return: None
    """
    import os

    import pyvfg

    basedir = os.path.join(os.path.dirname(__file__), "..", "payloads", "validate")
    with open(os.path.join(basedir, f), "r") as file:
        vfg_json = file.read()
        vfg = pyvfg.vfg_upgrade(vfg_json)
        with pytest.raises(pyvfg.ValidationErrors):
            pyvfg.validate_graph(vfg)


@pytest.mark.parametrize("f", ["post_validate_example.json"])
def test_validate_graph_success(f):
    """
    Tests graph validation, with the same procedure as gpil-pipeline.
    :return:
    """
    import os

    import pyvfg

    basedir = os.path.join(os.path.dirname(__file__), "..", "payloads", "validate")
    with open(os.path.join(basedir, f), "r") as file:
        vfg_json = file.read()
        vfg = pyvfg.vfg_upgrade(vfg_json)
        # NOTE: Change from the above! we want these to succeed at validation
        assert not pyvfg.validate_graph(vfg), "check for validity"


def test_vfg_from_json_invalid():
    import pyvfg

    invalid_vfg_json = {"version": "0.4.0", "variables": {}, "factors": {}}
    with pytest.raises(JsonSerializationError):
        _vfg = pyvfg.vfg_from_json(invalid_vfg_json)


def test_vfg_upgrade_invalid():
    import pyvfg

    invalid_vfg_json = 4.0
    with pytest.raises(AttributeError):
        _vfg = pyvfg.vfg_upgrade(invalid_vfg_json)


def test_vfg_upgrade_invalid_json():
    import pyvfg

    invalid_vfg_json = {"version": "0.4.0", "variables": {}, "factors": {}}
    with pytest.raises(JsonSerializationError):
        _vfg = pyvfg.vfg_upgrade(invalid_vfg_json)


if __name__ == "__main__":
    vfg_schema_dict, vfg_schema_json = vfg_to_json_schema()
    print(json.dumps(vfg_schema_dict, indent=2))
