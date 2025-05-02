# -*- coding: utf-8 -*-
import pyvfg


def test_validate_graph():
    """
    This verifies that `validate_graph` exists at top level. For tests of actual functionality,
    see test_vfg_0_4_0.py
    :return: None
    """
    assert "validate_graph" in pyvfg.__dict__.keys(), "validate graph is exported"
