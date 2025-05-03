r"""This module, examples_test.py, tests functionality of the included module.

Example
-------
source ~/autotwin/automesh/.venv/bin/activate
cd ~/autotwin/automesh/book/examples/unit_tests
python -m pytest examples_test.py -v  # -v is for verbose

to run a single test in this module, for example `test_hello` function:
python -m pytest examples_test.py::test_foo -v
"""

import pytest

import examples_figures as ff


def test_renumber():
    """Tests that the renumber function works as expected."""
    source = (300, 22, 1)
    old = (1, 22, 300, 40)
    new = (42, 2, 9, 1000)

    result = ff.renumber(source=source, old=old, new=new)
    assert result == (9, 2, 42)

    # Assure that tuples old and new of unequal length raise an AssertionError
    new = (42, 2)  # overwrite
    err = "Tuples `old` and `new` must have equal length."
    with pytest.raises(AssertionError, match=err):
        _ = ff.renumber(source=source, old=old, new=new)


def test_mesh_with_element_connectivity():
    """Test CubeMulti by hand."""
    gold_mesh_lattice_connectivity = (
        (
            2,
            (2, 3, 6, 5, 11, 12, 15, 14),
            (4, 5, 8, 7, 13, 14, 17, 16),
            (5, 6, 9, 8, 14, 15, 18, 17),
        ),
        (
            31,
            (11, 12, 15, 14, 20, 21, 24, 23),
        ),
        (
            44,
            (14, 15, 18, 17, 23, 24, 27, 26),
        ),
        (
            82,
            (1, 2, 5, 4, 10, 11, 14, 13),
        ),
    )
    gold_mesh_element_connectivity = (
        (
            2,
            (2, 3, 6, 5, 11, 12, 15, 14),
            (4, 5, 8, 7, 13, 14, 17, 16),
            (5, 6, 9, 8, 14, 15, 18, 17),
        ),
        (31, (11, 12, 15, 14, 19, 20, 22, 21)),
        (44, (14, 15, 18, 17, 21, 22, 24, 23)),
        (82, (1, 2, 5, 4, 10, 11, 14, 13)),
    )

    result = ff.mesh_element_connectivity(
        mesh_with_lattice_connectivity=gold_mesh_lattice_connectivity
    )

    assert result == gold_mesh_element_connectivity


def test_elements_no_block_ids():
    """Given a mesh, strips the block ids from the"""
    known_input = (
        (
            2,
            (2, 3, 6, 5, 11, 12, 15, 14),
            (4, 5, 8, 7, 13, 14, 17, 16),
            (5, 6, 9, 8, 14, 15, 18, 17),
        ),
        (31, (11, 12, 15, 14, 20, 21, 24, 23)),
        (44, (14, 15, 18, 17, 23, 24, 27, 26)),
        (82, (1, 2, 5, 4, 10, 11, 14, 13)),
    )

    gold_output = (
        (2, 3, 6, 5, 11, 12, 15, 14),
        (4, 5, 8, 7, 13, 14, 17, 16),
        (5, 6, 9, 8, 14, 15, 18, 17),
        (11, 12, 15, 14, 20, 21, 24, 23),
        (14, 15, 18, 17, 23, 24, 27, 26),
        (1, 2, 5, 4, 10, 11, 14, 13),
    )

    result = ff.elements_without_block_ids(mesh=known_input)

    assert result == gold_output
