import numpy as np
import pytest
import json
from jsonpatch import JsonPatch

import pyvfg
from pyvfg.versions.vfg_0_5_0 import (
    Variable,
    ModelType,
)
from pyvfg.errors import ValidationError, ValidationErrors
from pyvfg import (
    VFG,
    DiscreteVariableNamedElements,
    Distribution,
    Factor,
)


# Test error classes


def test_validation_error_construction():
    pass


def test_error_dict():
    pass


def test_error_patches_methods():
    error = pyvfg.MissingFactors(
        ["A"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["A"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )
    error2 = pyvfg.MissingFactors(
        ["B"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["B"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )

    error3 = pyvfg.MissingFactors(
        ["A"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["A"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )

    error4 = pyvfg.MissingFactors(
        ["B"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["B"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )

    ep = ValidationErrors(errors=[error, error2])
    ep2 = ValidationErrors(errors=[error3, error4])

    assert ep == ep2, "ValidationErrors should be equal"

    # Different exception value
    error5 = pyvfg.MissingFactors(
        ["C"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["A"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )
    # Different exception type
    error6 = pyvfg.StateVarMissingLikelihood(
        ["A"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["A"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )
    # Different jsonpatch
    error7 = pyvfg.MissingFactors(
        ["A"],
        JsonPatch(
            [
                {
                    "op": "add",
                    "path": "/factors/-",
                    "value": {
                        "variables": ["C"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                }
            ]
        ),
    )

    ep3 = ValidationErrors(errors=[error])
    ep4 = ValidationErrors(errors=[error5])
    ep5 = ValidationErrors(errors=[error6])
    ep6 = ValidationErrors(errors=[error7])

    assert (
        ep3 != ep4
    ), "ValidationErrors should not be equal if they have different exception values"
    assert (
        ep3 != ep5
    ), "ValidationErrors should not be equal if they have different exception types"
    assert (
        ep3 != ep6
    ), "ValidationErrors should not be equal if they have different patches"


def test_apply_patches():
    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[],
    )
    with pytest.raises(ValidationErrors):
        vfg.validate()

    json_patch1 = JsonPatch(
        [
            {
                "op": "add",
                "path": "/factors/-",
                "value": {
                    "variables": ["A"],
                    "distribution": "categorical",
                    "values": [0.5, 0.5],
                },
            }
        ]
    )
    json_patch2 = JsonPatch(
        [
            {
                "op": "add",
                "path": "/factors/-",
                "value": {
                    "variables": ["B"],
                    "distribution": "categorical",
                    "values": [0.5, 0.5],
                },
            }
        ]
    )
    error_patch = pyvfg.MissingFactors(["B"], json_patch2)

    fixed_vfg = vfg.apply_patches(json_patch1)
    assert len(fixed_vfg.factors) == 1
    assert fixed_vfg.factors[-1].variables == ["A"]

    with pytest.raises(ValidationErrors):
        fixed_vfg.validate()

    more_fixed_vfg = fixed_vfg.apply_patches(error_patch)
    assert len(more_fixed_vfg.factors) == 2
    assert more_fixed_vfg.factors[-1].variables == ["B"]

    assert not more_fixed_vfg.validate(), "Model should pass validation"


def test_zero_normalization_catgegorical_conditional():
    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.zeros((2, 2)),
            )
        ],
    )
    errors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.NormalizationError
    assert error.parameters["factor_idx"] == 0
    patch = json.loads(error.patch.to_string())
    assert patch[0]["op"] == "replace"
    assert patch[0]["path"] == "/factors/0/values"
    assert np.allclose(patch[0]["value"], np.ones((2, 2)) / 2)


def test_non_recoverable_errors():
    pass


# Generic facgor graph tests


def test_validate_as_factor_graph():
    """
    Tests that a valid factor graph passes validation
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B"],
                distribution=Distribution.Categorical,
                values=np.ones(2) / 2,
            ),
        ],
    )
    assert not vfg.validate(), "Model should pass validation"
    assert not vfg.validate_as(
        ModelType.FactorGraph
    ), "Model should pass validation as a Factor Graph"


def test_validate_factor_graph_multiple_warnings():
    """
    Tests that multiple warnings are captured and returned
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
            "D": Variable(DiscreteVariableNamedElements(elements=["d1", "d2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=[0.4],  # Incorrect shape - non-recoverable error
            ),
            Factor(
                variables=["A"],
                distribution=Distribution.Categorical,
                values=[],  # No values - recoverable by adding flat dist
            ),
            # We also have missing priors on "C" and "D"
        ],
    )
    with pytest.raises(ValidationErrors):
        vfg.validate()

    num_errors = 3
    num_recoverable = 2
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    errors: ValidationErrors = pyvfg.validate_graph(vfg, raise_exceptions=False)

    assert len(errors) == num_errors, f"There should be {num_errors} errors"
    errors_dicts = errors.to_dicts()
    error_parameters = [e.get("parameters") for e in errors_dicts]
    error_message = [e.get("message") for e in errors_dicts]
    assert "not connected" in error_message[0]
    assert "shape" in error_message[1] and "incompatible" in error_message[1]
    assert "probability value" in error_message[2]
    assert set(error_parameters[0]["variables"]) == set(["C", "D"])
    assert error_parameters[1]["factor_idx"] == 0
    assert error_parameters[2]["factor_idx"] == 1

    patches = errors.patches
    assert (
        len(patches) == num_recoverable
    ), f"There should be {num_recoverable} patches."

    # Test patches

    fixed_vfg = vfg.apply_patches(errors)
    assert np.allclose(fixed_vfg.factors[1].values, np.ones(2) / 2)
    assert np.allclose(fixed_vfg.factors[2].values, np.ones(2) / 2)
    assert np.allclose(fixed_vfg.factors[3].values, np.ones(2) / 2)


def test_validate_factor_graph_no_factors():
    """
    Tests errors on a factor graph with no factors
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
            "D": Variable(DiscreteVariableNamedElements(elements=["d1", "d2"])),
        },
        factors=[],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert (
        len(errors) == 1
    ), "There should be one error which collects the MissingFactor errors for all variables."
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.MissingFactors
    assert (
        len(list(error.patch)) == 4
    ), "There should be 4 patches, one for each variable."


def test_validate_factor_graph_empty_variable():
    """
    Tests errors on a factor graph with zero variable elements
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=[])),
        },
        factors=[
            Factor(
                variables=["A"],
                distribution=Distribution.Categorical,
                values=[0.0],
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert (
        len(errors) == 2
    ), "There should be two errors: one for the variable and one for the tensor"
    assert set([type(e) for e in errors]) == {
        pyvfg.InvalidVariableItemCount,
        pyvfg.IncorrectTensorShape,
    }


def test_validate_factor_graph_incorrect_tensor_shape():
    """
    Tests errors on a factor graph with an incorrect tensor shape
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
        },
        factors=[
            Factor(
                variables=["A"],
                distribution=Distribution.Categorical,
                values=[0.0],
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    assert set([type(e) for e in errors]) == {
        pyvfg.IncorrectTensorShape,
    }

    # Should be no patch as we can't infer how to fix the tensor
    assert len(errors.patches) == 0


def test_validate_factor_graph_incorrect_tensor_shape_missing_var():
    """
    Tests errors on a factor graph with an incorrect tensor shape and a missing variable
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.Potential,
                values=[0.0],
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    assert set([type(e) for e in errors]) == {
        pyvfg.VariableMissingInVariableList,
    }

    # Should be no patch as we can't infer the variable cardinality from the tensor shape
    assert len(errors.patches) == 0


def test_validate_factor_graph_no_variable():
    """
    Tests errors on a factor graph with a factor containing no variables
    """

    vfg = VFG(
        variables={},
        factors=[
            Factor(
                variables=[],
                distribution=Distribution.Categorical,
                values=[],
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert (
        len(errors) == 2
    ), "There should be two errors: one for the variable and one for the tensor"
    assert set([type(e) for e in errors]) == {
        pyvfg.MissingVariable,
        pyvfg.MissingProbability,
    }


def test_validate_factor_graph_missing_variable():
    """
    Tests errors on a factor graph with a factor that references a nonexistent variable
    """

    vfg = VFG(
        variables={},
        factors=[
            Factor(
                variables=["A"],
                distribution=Distribution.Categorical,
                values=[0.2, 0.4, 0.4],
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    assert set([type(e) for e in errors]) == {
        pyvfg.VariableMissingInVariableList,
    }

    # Test patch
    fixed_vfg = vfg.apply_patches(errors)
    assert "A" in fixed_vfg.variables
    assert fixed_vfg.variables["A"].cardinality == 3


def test_validate_factor_graph_missing_variable_no_values():
    """
    Tests errors on a factor graph with a factor that references a nonexistent variable
    when the tensor is also empty
    """

    vfg = VFG(
        variables={},
        factors=[
            Factor(
                variables=["A"],
                distribution=Distribution.Categorical,
                values=[],
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert (
        len(errors) == 2
    ), "There should be two errors: one for the variable and one for the tensor"
    assert set([type(e) for e in errors]) == {
        pyvfg.VariableMissingInVariableList,
        pyvfg.MissingProbability,
    }


def test_validate_factor_graph_fill_in_missing_factor():
    """
    Tests auto-correct: Missing tensor values in a factor graph can be filled in
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=[],  # Missing values
            ),
        ],
    )
    with pytest.raises(ValidationErrors):
        vfg.validate()

    errors: ValidationErrors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.MissingProbability
    errors_dict = error.to_dict()
    error_parameters = errors_dict.get("parameters")
    assert error_parameters is not None, "Error parameters should be present"
    error_message = errors_dict.get("message")
    assert error_message is not None, "Error message should be present"
    assert "probability value" in error_message
    assert error_parameters["factor_idx"] == 0

    fixed_vfg = vfg.apply_patches(errors)
    assert np.allclose(fixed_vfg.factors[0].values, np.ones((2, 2)) / 2)


# Bayesian Network tests


def test_validate_bayes_net_cyclic_positive_direct():
    """
    Tests that a cyclic Bayesian Network A<--B<--A is detected
    """
    import pyvfg

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B", "A"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate_as(
        ModelType.BayesianNetwork, raise_exceptions=False
    )
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.CyclicGraph


def test_validate_bayes_net_cyclic_positive_indirect():
    """
    Tests that a cyclic Bayesian Network A<--B<--C<--A is detected
    """
    import pyvfg

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B", "C"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["C", "A"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )
    errors: ValidationErrors = vfg.validate_as(
        ModelType.BayesianNetwork, raise_exceptions=False
    )
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.CyclicGraph


def test_validate_bayes_net_cyclic_negative():
    """
    Tests that a non-cyclic Bayesian Network does not throw a CyclicGraph error
    """
    import pyvfg

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B", "C"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["C"],
                distribution=Distribution.Categorical,
                values=np.ones(2) / 2,
            ),
        ],
    )
    assert not vfg.validate_as(
        ModelType.BayesianNetwork
    ), "Model should pass validation"


def test_validate_bayes_net_missing_conditional():
    """
    Tests that a Bayesian Network with a missing CPD (conditional probability distribution) is detected
    """
    import pyvfg

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )
    with pytest.raises(ValidationErrors):
        vfg.validate_as(ModelType.BayesianNetwork)

    assert (
        not vfg.validate()
    ), "Model should not fail validation when evaluated as a generic factor graph."

    errors = vfg.validate_as(ModelType.BayesianNetwork, raise_exceptions=False)

    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    errors_dict = error.to_dict()
    error_parameters = errors_dict.get("parameters")
    assert error_parameters is not None, "Error parameters should be present"
    error_message = errors_dict.get("message")
    assert error_message is not None, "Error message should be present"
    assert "distribution" in error_message
    assert error_parameters["variable"] == ["B"]

    # Test patches
    fixed_vfg: VFG = vfg.apply_patches(errors)
    assert fixed_vfg.factors[1].distribution == Distribution.Categorical


def test_validate_bayes_net_fix_distribution_type():
    """
    Tests that a factor involving multiple variables in a Bayes net can be autocorrected
    to use the conditional distribution type
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.Categorical,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
            ),
        ],
    )
    with pytest.raises(ValidationErrors):
        vfg.validate_as(ModelType.BayesianNetwork)

    errors = vfg.validate_as(ModelType.BayesianNetwork, raise_exceptions=False)

    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    errors_dict = error.to_dict()
    error_parameters = errors_dict.get("parameters")
    assert error_parameters is not None, "Error parameters should be present"
    error_message = errors_dict.get("message")
    assert error_message is not None, "Error message should be present"
    assert "conditional" in error_message
    assert error_parameters["variable"] == ["A", "B"]

    # Check deltas
    fixed_vfg = vfg.apply_patches(errors)
    assert fixed_vfg.factors[0].distribution == Distribution.CategoricalConditional


def test_validate_bayes_net_invalid_factor_role():
    """
    Tests that a factor with an invalid role in a Bayes net is detected
    """

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Preference,
            ),
            Factor(
                variables=["B"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
            ),
        ],
    )
    with pytest.raises(ValidationErrors):
        vfg.validate_as(ModelType.BayesianNetwork)

    errors = vfg.validate_as(ModelType.BayesianNetwork, raise_exceptions=False)

    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    errors_dict = error.to_dict()
    error_parameters = errors_dict.get("parameters")
    assert error_parameters is not None, "Error parameters should be present"
    error_message = errors_dict.get("message")
    assert error_message is not None, "Error message should be present"
    assert "role" in error_message
    assert error_parameters["variables"] == ["A", "B"]
    assert error_parameters["role"] == pyvfg.FactorRole.Preference

    # Test patches
    fixed_vfg = vfg.apply_patches(errors)
    assert fixed_vfg.factors[0].role is None

    assert (
        not vfg.validate()
    ), "Model should pass if evaluated as a generic factor graph"


def test_validate_bayes_net_unnormalized_conditional_distribution():
    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)),
            ),
            Factor(
                variables=["B"],
                distribution=Distribution.Categorical,
                values=np.array([0.5, 0.5]),
            ),
        ],
    )
    errors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.NormalizationError
    errors_dict = error.to_dict()
    error_parameters = errors_dict.get("parameters")
    assert error_parameters is not None, "Error parameters should be present"
    error_message = errors_dict.get("message")
    assert error_message is not None, "Error message should be present"
    assert "conditional" in error_message


# MRF tests


def test_validate_mrf_valid():
    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
            "D": Variable(DiscreteVariableNamedElements(elements=["d1", "d2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B", "C", "D"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2, 2)) / 2,
            ),
            Factor(
                variables=["C", "A"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )
    assert not vfg.validate_as(
        ModelType.MarkovRandomField
    ), "Model should pass validation"


def test_validate_mrf_invalid_conditional_distribution():

    conditional_values = np.ones((2, 4))
    conditional_values /= conditional_values.sum(axis=0)
    conditional_values = np.reshape(conditional_values, (2, 2, 2))

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
            "D": Variable(DiscreteVariableNamedElements(elements=["d1", "d2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B", "C", "D"],
                distribution=Distribution.CategoricalConditional,
                values=conditional_values,
            ),
            Factor(
                variables=["C", "A"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )

    errors: ValidationErrors = vfg.validate_as(
        ModelType.MarkovRandomField, raise_exceptions=False
    )
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.NonPotentialInMRF


def test_validate_mrf_negative_potential():
    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) * -1,
            ),
        ],
    )
    errors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.NegativePotentialError


# POMDP tests


def test_validate_pomdp_no_transition():
    """
    Tests that a POMDP without a transition factor is detected
    """

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["obs"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
                role=pyvfg.FactorRole.Preference,
            ),
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    assert pyvfg.NoTransitionFactors in [type(e) for e in errors]


def test_validate_pomdp_unlabeled_obs_likelihood():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
        },
        factors=[
            Factor(
                variables=["obs"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
                role=pyvfg.FactorRole.Preference,
            ),
            Factor(
                variables=["state", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )

    with pytest.raises(ValidationErrors):
        vfg.validate_as(ModelType.Pomdp)

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)

    assert len(errors) == 1, "There should be one error"
    errors_dicts = errors.to_dicts()
    error_parameters = [e.get("parameters") for e in errors_dicts]
    assert error_parameters, "Error parameters should be present"
    error_message = [e.get("message") for e in errors_dicts]
    assert error_message, "Error message should be present"
    assert all(["likelihood" in e for e in error_message])
    assert [error_parameters[0]["variables"] == ["obs", "state"]]

    # Test patches
    fixed_vfg = vfg.apply_patches(errors)
    assert fixed_vfg.factors[-1].role == pyvfg.FactorRole.Likelihood

    assert (
        not vfg.validate()
    ), "Model should pass if evaluated as a generic factor graph"


def test_validate_pomdp_missing_obs_likelihood():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
        },
        factors=[
            Factor(
                variables=["obs"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
                role=pyvfg.FactorRole.Preference,
            ),
            Factor(
                variables=["state", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
        ],
    )

    with pytest.raises(ValidationErrors):
        vfg.validate_as(ModelType.Pomdp)

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    errors_dicts = errors.to_dicts()
    error_parameters = [e.get("parameters") for e in errors_dicts]
    assert error_parameters, "Error parameters should be present"
    error_message = [e.get("message") for e in errors_dicts]
    assert error_message, "Error message should be present"
    assert all(["likelihood" in e for e in error_message])
    assert [error_parameters[0]["variables"] == ["obs", "state"]]

    # Test patches
    fixed_vfg = vfg.apply_patches(errors)
    new_factor = fixed_vfg.factors[-1]
    assert (
        new_factor.role == pyvfg.FactorRole.Likelihood
    ), "Incorrect role on patched factor"
    assert new_factor.variables == ["obs", "state"]

    assert (
        not vfg.validate()
    ), "Model should pass if evaluated as a generic factor graph"


def test_validate_pomdp_unlabeled_state_likelihood():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    expected_error_types = set(
        [
            pyvfg.StateVarMissingLikelihood,
        ]
    )
    actual_error_types = set([type(e) for e in errors])

    missing_errors = expected_error_types - actual_error_types
    extra_errors = actual_error_types - expected_error_types

    assert len(missing_errors) == 0, f"Missing errors: {missing_errors}"
    assert len(extra_errors) == 0, f"Extra errors: {extra_errors}"

    fixed_vfg, errors = vfg.correct(
        as_model_type=ModelType.Pomdp, raise_exceptions=False
    )
    assert not errors, "There should be no errors"
    assert fixed_vfg.factors[-1].role == pyvfg.FactorRole.Likelihood


def test_validate_pomdp_missing_transition():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
        },
        factors=[
            Factor(
                variables=["obs"],
                distribution=Distribution.Categorical,
                values=[0.5, 0.5],
                role=pyvfg.FactorRole.Preference,
            ),
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Likelihood,
            ),
        ],
    )

    with pytest.raises(ValidationErrors):
        vfg.validate_as(ModelType.Pomdp)

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)

    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    errors_dict = error.to_dict()
    error_parameters = errors_dict.get("parameters")
    assert error_parameters, "Error parameters should be present"
    error_message = errors_dict.get("message")
    assert error_message, "Error message should be present"
    assert "transition" in error_message
    assert error_parameters["variables"] == ["state"]

    # Test patches
    fixed_vfg = vfg.apply_patches(errors)
    new_factor = fixed_vfg.factors[-1]
    assert (
        new_factor.role == pyvfg.FactorRole.Transition
    ), "Incorrect role on patched factor"
    assert new_factor.variables == ["state", "state"]

    assert (
        not vfg.validate()
    ), "Model should pass if evaluated as a generic factor graph"


def test_validate_pomdp_cannot_infer_variable_type():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
        ],
    )
    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    assert len(errors) == 4, "There should be four errors"
    error_types = set([type(e) for e in errors])
    assert error_types == {
        pyvfg.StateVarMissingLikelihood,
        pyvfg.VariableRoleIndeterminate,
        pyvfg.MissingFactors,
        pyvfg.NoLikelihoodFactors,
    }


def test_validate_pomdp_mislabeled_transition_distribution():
    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.Categorical,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.Categorical,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Likelihood,
            ),
        ],
    )
    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    assert len(errors) == 2, "There should be one error"
    error_types = set([type(e) for e in errors])
    assert error_types == {pyvfg.MultivariateDistributionNotConditional}

    fixed_vfg = vfg.apply_patches(errors)
    assert fixed_vfg.factors[0].distribution == Distribution.CategoricalConditional
    assert fixed_vfg.factors[1].distribution == Distribution.CategoricalConditional


# Autocorrect tests


def test_correct_graph_valid_bayes_net():

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B"],
                distribution=Distribution.Categorical,
                values=np.ones(2) / 2,
            ),
        ],
    )
    corrected_vfg, errors = vfg.correct()
    assert not errors, "There should be no errors"
    assert corrected_vfg == vfg

    corrected_as_bayes_net, errors = vfg.correct(
        as_model_type=ModelType.BayesianNetwork
    )
    assert not errors, "There should be no errors"
    assert corrected_as_bayes_net == vfg


def test_correct_graph_invalid_bayes_net():

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )
    corrected_vfg, errors = vfg.correct()
    assert not errors, "There should be no errors"
    assert corrected_vfg == vfg

    corrected_as_bayes_net, errors = vfg.correct(
        as_model_type=ModelType.BayesianNetwork, raise_exceptions=False
    )
    assert not errors, "There should be no errors"
    assert corrected_as_bayes_net.factors[-1].distribution == Distribution.Categorical
    assert np.allclose(corrected_as_bayes_net.factors[-1].values, np.ones(2) / 2)
    assert corrected_as_bayes_net.factors[-1].role is None
    assert corrected_as_bayes_net.factors[-1].variables == ["B"]


def test_correct_graph_normalization_error():
    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) * 4,
            ),
        ],
    )
    errors = vfg.validate(raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error: ValidationError = errors[0]
    assert type(error) == pyvfg.NormalizationError
    assert error.parameters["factor_idx"] == 0

    _, errors = vfg.correct(raise_exceptions=False)
    assert not errors, "There should be no errors"


def test_correct_graph_valid_pomdp():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Likelihood,
            ),
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
        ],
    )

    assert not vfg.validate_as(ModelType.Pomdp), "Model should pass validation"
    fixed_vfg, errors = vfg.correct(as_model_type=ModelType.Pomdp)
    assert not errors, "There should be no errors"
    assert fixed_vfg == vfg


def test_correct_mab_vfg(mab_vfg: VFG):

    assert not mab_vfg.validate_as(ModelType.Pomdp), "Model should pass validation"
    fixed_vfg, errors = mab_vfg.correct(as_model_type=ModelType.Pomdp)
    assert not errors, "There should be no errors"
    assert fixed_vfg == mab_vfg


def test_correct_invalid_mab_vfg(mab_vfg: VFG):

    # Remove role label from a likelihood
    mab_vfg_error = mab_vfg.deepcopy()
    mab_vfg_error.factors[2].role = None
    errors = mab_vfg_error.validate_as(ModelType.Pomdp, raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error_types = set([type(e) for e in errors])
    assert pyvfg.ObsVarMissingLikelihood in error_types
    fixed_vfg, errors = mab_vfg_error.correct(as_model_type=ModelType.Pomdp)
    assert not errors, "There should be no errors"

    assert fixed_vfg == mab_vfg


def test_correct_graph_invalid_pomdp_unfixable():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
        ],
    )

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    expected_error_types = set(
        [
            pyvfg.VariableRoleIndeterminate,
            pyvfg.MissingFactors,
            pyvfg.StateVarMissingLikelihood,
            pyvfg.NoLikelihoodFactors,
        ]
    )
    actual_error_types = set([type(e) for e in errors])

    missing_errors = expected_error_types - actual_error_types
    extra_errors = actual_error_types - expected_error_types

    assert len(missing_errors) == 0, f"Missing errors: {missing_errors}"
    assert len(extra_errors) == 0, f"Extra errors: {extra_errors}"

    _, errors = vfg.correct(as_model_type=ModelType.Pomdp, raise_exceptions=False)
    assert len(errors) == 2, "There should be two errors"
    error_types = set([type(e) for e in errors])
    assert pyvfg.VariableRoleIndeterminate in error_types
    assert pyvfg.NoLikelihoodFactors in error_types


def test_correct_graph_invalid_pomdp_fixable():

    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )

    errors = vfg.validate_as(ModelType.Pomdp, raise_exceptions=False)
    expected_error_types = set(
        [
            pyvfg.StateVarMissingLikelihood,
        ]
    )
    actual_error_types = set([type(e) for e in errors])

    missing_errors = expected_error_types - actual_error_types
    extra_errors = actual_error_types - expected_error_types

    assert len(missing_errors) == 0, f"Missing errors: {missing_errors}"
    assert len(extra_errors) == 0, f"Extra errors: {extra_errors}"

    _, errors = vfg.correct(as_model_type=ModelType.Pomdp, raise_exceptions=False)
    assert len(errors) == 0, "There should be no errors"


def test_check_model_is_one_of_pomdp():
    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2)) / 2,
                role=pyvfg.FactorRole.Likelihood,
            ),
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
        ],
    )

    assert vfg.model_is_one_of(ModelType.Pomdp), "Model was not recognized as a POMDP"
    assert not vfg.model_is_one_of(
        ModelType.BayesianNetwork
    ), "Model was incorrectly recognized as a Bayesian Network"
    assert not vfg.model_is_one_of(
        ModelType.MarkovRandomField
    ), "Model was incorrectly recognized as a Markov Random Field"
    assert vfg.model_is_one_of(
        ModelType.FactorGraph
    ), "Model should pass as a generic factor graph"
    assert not vfg.model_is_one_of(
        [ModelType.MarkovRandomField, ModelType.BayesianNetwork]
    ), "Model should not pass as either BN or MRF"


def test_check_model_is_one_of_invalid_pomdp():
    vfg = VFG(
        variables={
            "obs": Variable(DiscreteVariableNamedElements(elements=["o1", "o2"])),
            "state": Variable(DiscreteVariableNamedElements(elements=["s1", "s2"])),
            "control": Variable(DiscreteVariableNamedElements(elements=["c1"])),
        },
        factors=[
            Factor(
                variables=["obs", "state"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2)) / 2,  # Wrong shape
                # Missing role
            ),
            Factor(
                variables=["state", "state", "control"],
                distribution=Distribution.CategoricalConditional,
                values=np.ones((2, 2, 1)) / 2,
                role=pyvfg.FactorRole.Transition,
            ),
        ],
    )

    assert vfg.model_is_one_of(ModelType.Pomdp), "Model was not recognized as a POMDP"
    assert not vfg.model_is_one_of(
        ModelType.BayesianNetwork
    ), "Model was incorrectly recognized as a Bayesian Network"
    assert not vfg.model_is_one_of(
        ModelType.MarkovRandomField
    ), "Model was incorrectly recognized as a Markov Random Field"
    assert vfg.model_is_one_of(
        ModelType.FactorGraph
    ), "Model should pass as a generic factor graph"
    assert not vfg.model_is_one_of(
        [ModelType.MarkovRandomField, ModelType.BayesianNetwork]
    ), "Model should not pass as either BN or MRF"


def test_check_model_is_one_of_bayes_net(sprinkler_vfg: VFG):

    assert sprinkler_vfg.model_is_one_of(
        ModelType.BayesianNetwork
    ), "Model was not recognized as a Bayesian Network"
    assert not sprinkler_vfg.model_is_one_of(
        ModelType.Pomdp
    ), "Model was incorrectly recognized as a POMDP"
    assert not sprinkler_vfg.model_is_one_of(
        ModelType.MarkovRandomField
    ), "Model was incorrectly recognized as a Markov Random Field"
    assert sprinkler_vfg.model_is_one_of(
        ModelType.FactorGraph
    ), "Model should pass as a generic factor graph"
    assert not sprinkler_vfg.model_is_one_of(
        [ModelType.MarkovRandomField, ModelType.Pomdp]
    ), "Model should not pass as either POMDP or MRF"


def test_check_model_is_one_of_mrf():

    vfg = VFG(
        variables={
            "A": Variable(DiscreteVariableNamedElements(elements=["a1", "a2"])),
            "B": Variable(DiscreteVariableNamedElements(elements=["b1", "b2"])),
            "C": Variable(DiscreteVariableNamedElements(elements=["c1", "c2"])),
            "D": Variable(DiscreteVariableNamedElements(elements=["d1", "d2"])),
        },
        factors=[
            Factor(
                variables=["A", "B"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) / 2,
            ),
            Factor(
                variables=["B", "C", "D"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2, 2)) / 2,
            ),
            Factor(
                variables=["C", "A"],
                distribution=Distribution.Potential,
                values=np.ones((2, 2)) / 2,
            ),
        ],
    )

    assert not vfg.model_is_one_of(
        ModelType.Pomdp
    ), "Model was incorrectly recognized as a POMDP"
    assert not vfg.model_is_one_of(
        ModelType.BayesianNetwork
    ), "Model was incorrectly recognized as a Bayesian Network"
    assert vfg.model_is_one_of(
        ModelType.MarkovRandomField
    ), "Model was not recognized as a Markov Random Field"
    assert vfg.model_is_one_of(
        ModelType.FactorGraph
    ), "Model should pass as a generic factor graph"
    assert not vfg.model_is_one_of(
        [ModelType.Pomdp, ModelType.BayesianNetwork]
    ), "Model should not pass as either POMDP or BN"


def test_validation_errors_messages():
    error = pyvfg.MissingVariable(factor_idx=1)
    error2 = pyvfg.InvalidFactorRole(
        which_vars=["A", "B"],
        role=pyvfg.FactorRole.Preference,
        patch=JsonPatch([{"op": "replace", "path": "/role", "value": 3}]),
    )
    errors = pyvfg.ValidationErrors([error, error2])

    try:
        raise error
    except pyvfg.ValidationError as e:
        errors_json = json.loads(str(e))
        assert isinstance(errors_json, dict)
        assert errors_json.get("message") == "Factor 1 must have at least one variable."
        assert errors_json.get("parameters") == {"factor_idx": 1}

    try:
        raise error2
    except pyvfg.InvalidFactorRole as e:
        errors_json = json.loads(str(e))
        assert isinstance(errors_json, dict)
        assert (
            errors_json.get("message")
            == "Factors involving variable(s) 'A, B' have role 'FactorRole.Preference' which is undefined for this model type."
        )
        assert errors_json.get("parameters") == {
            "variables": ["A", "B"],
            "role": "preference",
        }

    assert len(errors) == 2

    try:
        raise errors
    except pyvfg.ValidationErrors as e:
        errors_json = json.loads(str(e))

        # Check dict conversion while we're at it
        md = e.to_dict()
        assert isinstance(md, dict)
        md2 = e.to_dicts()
        assert isinstance(md2, list)

        e1_json_dict = json.loads(str(error))
        e2_json_dict = json.loads(str(error2))
        assert isinstance(errors_json, dict)
        assert errors_json.get("errors") == [e1_json_dict, e2_json_dict]


def test_validation_invlid_graph_two_factors_gpil_615():

    vfg = VFG.from_file(
        "packages/gpil/tests/fixtures/models/invalid_vfg_two_factors_one_var.json"
    )

    errors = vfg.validate_as("bayesian_network", raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error = errors[0]
    # Added new distribution type to handle this error
    assert isinstance(error, pyvfg.MultipleDistributions)

    # Check that the error message is correct
    assert (
        "There must be only one distribution over variable"
        in error.to_dict()["message"]
    )
    assert "Factors targeting this variable" in error.to_dict()["message"]
    assert len(error.to_dict()["parameters"]) == 2


def test_validation_invlid_graph_three_factor_correct():
    vfg = VFG.model_validate(
        {
            "variables": {
                "A": {"elements": ["a1", "a2"]},
                "B": {"elements": ["b1", "b2", "b3", "b4"]},
                "C": {"elements": ["c1", "c2", "c3"]},
                "D": {"elements": ["d1", "d2", "d3", "d4", "d5"]},
                "E": {"elements": ["e1", "e2"]},
            },
            "factors": [
                {
                    "variables": ["B"],
                    "distribution": "categorical",
                    "values": np.ones((4)) / 4,
                },
                {
                    "variables": ["C"],
                    "distribution": "categorical",
                    "values": np.ones((3)) / 3,
                },
                {
                    "variables": ["D"],
                    "distribution": "categorical",
                    "values": np.ones((5)) / 5,
                },
                {
                    "variables": ["E"],
                    "distribution": "categorical",
                    "values": np.ones((2)) / 2,
                },
                {
                    "variables": ["A", "B"],
                    "distribution": "categorical_conditional",
                    "values": np.ones((2, 4)) / 2,
                },
                {
                    "variables": ["A", "C", "D"],
                    "distribution": "categorical_conditional",
                    "values": np.ones((2, 3, 5)) / 2,
                },
                {
                    "variables": ["A", "E"],
                    "distribution": "categorical_conditional",
                    "values": np.array([[0.8, 0.7], [0.2, 0.3]]),
                },
            ],
        }
    )

    errors = vfg.validate_as("bayesian_network", raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error = errors[0]
    assert isinstance(error, pyvfg.MultipleDistributions)
    error_dict = error.to_dict()
    assert (
        len(error_dict["parameters"]) == 2
    ), "There should be two parameters in the error message"
    assert (
        error_dict["parameters"]["variable"] == "A"
    ), "The variable referenced in the error message should be A"
    assert (
        len(error_dict["parameters"]["factor_idxs"]) == 3
    ), "Three factors should be referenced in the error message"

    model, errors = vfg.correct(
        as_model_type=pyvfg.ModelType.BayesianNetwork, raise_exceptions=False
    )
    bn = pyvfg.BayesianNetwork.from_vfg(model)
    assert len(errors) == 0, "There should be no errors when the model is corrected"
    factor = bn.get_factor("A")
    assert factor.values.shape == (
        2,
        4,
        3,
        5,
        2,
    ), "The values should be a tensor of shape (2, 4, 3, 5, 2)"
    assert np.allclose(
        factor.values[:, 0, 0, 0, 0], np.array([0.8, 0.2])
    ), "The values should be the same as the original values"


def test_validation_invlid_graph_three_factor_correct_with_common_vars():
    vfg = VFG.model_validate(
        {
            "variables": {
                "A": {"elements": ["a1", "a2"]},
                "B": {"elements": ["b1", "b2", "b3", "b4"]},
            },
            "factors": [
                {
                    "variables": ["B"],
                    "distribution": "categorical",
                    "values": np.ones((4)) / 4,
                },
                {
                    "variables": ["A", "B"],
                    "distribution": "categorical_conditional",
                    "values": np.ones((2, 4)) / 2,
                },
                {
                    "variables": ["A", "B"],
                    "distribution": "categorical_conditional",
                    "values": np.ones((2, 4)) / 2,
                },
            ],
        }
    )

    errors = vfg.validate_as("bayesian_network", raise_exceptions=False)
    assert len(errors) == 1, "There should be one error"
    error = errors[0]
    assert isinstance(error, pyvfg.MultipleDistributions)
    error_dict = error.to_dict()
    assert (
        len(error_dict["parameters"]) == 2
    ), "There should be two parameters in the error message"
    assert (
        error_dict["parameters"]["variable"] == "A"
    ), "The variable referenced in the error message should be A"
    assert (
        not "patch" in error_dict["parameters"]
    ), "No patch should be included in the error message"


def test_validation_invlid_graph_three_factor_correct_with_mismatched_shapes():
    vfg = VFG.model_validate(
        {
            "variables": {
                "A": {"elements": ["a1", "a2"]},
                "B": {"elements": ["b1", "b2", "b3", "b4"]},
            },
            "factors": [
                {
                    "variables": ["B"],
                    "distribution": "categorical",
                    "values": np.ones((4)) / 4,
                },
                {
                    "variables": ["A", "B"],
                    "distribution": "categorical_conditional",
                    "values": np.ones((2, 4)) / 2,
                },
                {
                    "variables": ["A", "B"],
                    "distribution": "categorical_conditional",
                    "values": np.ones((3, 4)) / 2,
                },
            ],
        }
    )

    errors = vfg.validate_as("bayesian_network", raise_exceptions=False)
    assert len(errors) == 2, "There should be two errors"
    assert set([type(e) for e in errors]) == {
        pyvfg.MultipleDistributions,
        pyvfg.IncorrectTensorShape,
    }, "There should be two errors"
