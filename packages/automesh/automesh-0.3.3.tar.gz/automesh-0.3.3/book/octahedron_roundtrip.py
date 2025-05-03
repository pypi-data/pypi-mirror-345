"""The purpose of this module is to show that the
segmentation data encoded in two .npy files is the same.
"""

import numpy as np

aa = np.load("octahedron.npy")
print(aa)

bb = np.load("octahedron3.npy")
print(bb)

comparison = aa == bb
print(comparison)
result = np.all(comparison)
print(f"Element-by-element equality is {result}.")
