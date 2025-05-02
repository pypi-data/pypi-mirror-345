from pyvfg.versions.vfg_0_5_0 import (
    VFG,
    DiscreteVariableAnonymousElements,
    DiscreteVariableNamedElements,
    Distribution,
    Factor,
    FactorRole,
    Metadata,
    ModelType,
    Variable,
    VariableRole,
)


def test_variable_named_elements():
    # Test with named elements
    named_var = Variable.model_validate(
        DiscreteVariableNamedElements(
            elements=["sunny", "rainy", "cloudy"], role=VariableRole.Latent
        )
    )
    assert named_var.elements == ["sunny", "rainy", "cloudy"]


def test_variable_anonymous_elements():
    # Test with anonymous elements (cardinality-based)
    anon_var = Variable.model_validate(
        DiscreteVariableAnonymousElements(cardinality=3, role=VariableRole.ControlState)
    )
    assert anon_var.elements == ["0", "1", "2"]


def test_variable_get_elements_method():
    # Test that get_elements() returns the same as the elements property
    named_var = Variable.model_validate(
        DiscreteVariableNamedElements(elements=["a", "b", "c"])
    )
    assert named_var.get_elements() == named_var.elements

    anon_var = Variable.model_validate(DiscreteVariableAnonymousElements(cardinality=2))
    assert anon_var.get_elements() == anon_var.elements


import json

import numpy as np
import pytest
from tests.conftest import get_json


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
        "tests/fixtures/models/sprinkler/sprinkler_vfg_0_5_0.json",
        "tests/fixtures/models/insurance/insurance_vfg_0_5_0.json",
    ],
)
def test_vfg_050_from_json(full_path):
    vfg_json = get_json(full_path)
    vfg = VFG(**vfg_json)

    vfg_dict = vfg.to_dict()

    assert vfg_dict == vfg_json


def test_vfg_050_init(variables_1, factors_1):
    # init with variables and factors
    vfg = VFG(variables=variables_1, factors=factors_1)
    vfg_dict = vfg.to_dict()
    assert vfg_dict["variables"] == variables_1
    assert vfg_dict["factors"][0]["variables"] == factors_1[0]["variables"]
    assert vfg_dict["factors"][0]["distribution"] == factors_1[0]["distribution"]
    assert vfg_dict["factors"][0]["values"] == factors_1[0]["values"]
    assert vfg_dict["factors"][0]["role"] == factors_1[0]["role"]


def test_vfg_050_init_default():
    vfg = VFG()
    assert vfg.variables == {}
    assert vfg.factors == []


def test_vfg_050_distribution_serialization():
    # Create a VFG with a factor using Distribution enum
    factor = Factor(
        variables=["x"],
        distribution=Distribution.Categorical,
        values=[0.5, 0.5],
    )
    vfg = VFG(factors=[factor])

    # Test that we can serialize to JSON
    vfg_dict = vfg.to_dict()
    json_str = json.dumps(vfg_dict)

    # Parse back from JSON and verify the distribution value
    parsed_dict = json.loads(json_str)
    assert parsed_dict["factors"][0]["distribution"] == "categorical"

    # Verify we can deserialize back to VFG
    vfg_from_dict = VFG.from_dict(parsed_dict)
    assert vfg_from_dict.factors[0].distribution == Distribution.Categorical


def test_vfg_050_all_enum_serialization():
    # Create a VFG with all possible enum types
    factor = Factor(
        variables=["x"],
        distribution=Distribution.Categorical,
        values=[0.5, 0.5],
        role=FactorRole.Transition,
    )

    variable = DiscreteVariableNamedElements(
        elements=["a", "b"], role=VariableRole.ControlState
    )

    metadata = Metadata(model_type=ModelType.BayesianNetwork, model_version="1.0")

    vfg = VFG(metadata=metadata, variables={"x": variable}, factors=[factor])

    # Test that we can serialize to JSON
    vfg_dict = vfg.to_dict()
    json_str = json.dumps(vfg_dict)

    # Parse back from JSON and verify all enum values
    parsed_dict = json.loads(json_str)

    # Check all enum values are correctly serialized
    assert parsed_dict["metadata"]["model_type"] == "bayesian_network"
    assert parsed_dict["variables"]["x"]["role"] == "control_state"
    assert parsed_dict["factors"][0]["distribution"] == "categorical"
    assert parsed_dict["factors"][0]["role"] == "transition"

    # Verify we can deserialize back to VFG with correct enum values
    vfg_from_dict = VFG.from_dict(parsed_dict)
    assert vfg_from_dict.metadata.model_type == ModelType.BayesianNetwork
    assert vfg_from_dict.variables["x"].root.role == VariableRole.ControlState
    assert vfg_from_dict.factors[0].distribution == Distribution.Categorical
    assert vfg_from_dict.factors[0].role == FactorRole.Transition


def test_vfg_json():
    """
    Tests reflexive conversion for a 3-deep nested tensor
    """
    import pyvfg

    vfg = VFG(
        variables={
            "var_elements": Variable(
                DiscreteVariableNamedElements(
                    elements=["a", "b"], role=VariableRole.Latent
                ),
            ),
            "var_other_elements": Variable(
                DiscreteVariableNamedElements(elements=["x", "y"]),
            ),
            "var_cardinality": Variable(
                DiscreteVariableAnonymousElements(
                    cardinality=2, role=VariableRole.Latent
                ),
            ),
        },
        factors=[
            Factor(
                variables=["var_elements", "var_cardinality", "var_other_elements"],
                distribution=Distribution.Potential,
                values=np.array(
                    [
                        [[0.1, 0.2], [0.3, 0.4]],
                        [[0.5, 0.6], [0.7, 0.8]],
                    ]
                ),
            ),
            Factor(
                variables=["var_other_elements"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
            ),
        ],
    )
    vfg.validate(raise_exceptions=True)
    vfg_json = vfg.model_dump_json()
    vfg_round_trip = pyvfg.vfg_upgrade(vfg_json)
    assert vfg == vfg_round_trip
