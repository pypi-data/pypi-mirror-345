r"""This module, examples_types.py, defines types used
for unit test examples.
"""

from typing import NamedTuple

import numpy as np


class Example(NamedTuple):
    """A base class that has all of the fields required to specialize into a
    specific example."""

    figure_title: str = "Figure Title"
    file_stem: str = "filename"
    segmentation = np.array(
        [
            [
                [
                    1,
                ],
            ],
        ],
        dtype=np.uint8,
    )
    included_ids = (1,)
    gold_lattice = None
    gold_mesh_lattice_connectivity = None
    gold_mesh_element_connectivity = None
