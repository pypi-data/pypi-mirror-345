"""This module creates a tetrahedral element and converts into four
hexahderal elements.
"""

import numpy as np

from tet_to_hex_types import Vertex, VertexSpherical

# Constant to convert radians to degrees
RAD_TO_DEG = 180.0 / np.pi
DEG_TO_RAD = np.pi / 180.0


def spherical_to_cartesian(vs: VertexSpherical) -> Vertex:
    """Convert spherical coordinates to Cartesian coordinates.

    Parameters:
    vs (VertexSpherical): An instance of VertexSpherical containing the
        spherical coordinates:

    Returns:
    Vertex: An instance of Vertex containing the Cartesian coordinates
        (x, y, z).
    """
    r, theta, phi = vs.r, vs.theta, vs.phi
    polar, azimuthal = theta * DEG_TO_RAD, phi * DEG_TO_RAD

    x = r * np.sin(polar) * np.cos(azimuthal)
    y = r * np.sin(polar) * np.sin(azimuthal)
    z = r * np.cos(polar)
    return Vertex(x, y, z)


def main():
    """
    Main function to demonstrate the conversion of spherical coordinates to
    Cartesian coordinates.
    """
    # Example spherical coordinates
    r = 1.0  # Radius of the sphere
    theta = 45.0  # degrees, polar angle
    phi = 60.0  # degrees, azimuthal angle

    # Convert to Cartesian coordinates
    cartesian_coords = spherical_to_cartesian(VertexSpherical(r, theta, phi))

    # Print the results
    print(f"Spherical Coordinates (r={r}, theta={theta}, phi={phi})")
    print("Cartesian Coordinates:")
    print(f"x={cartesian_coords.x}")
    print(f"y={cartesian_coords.y}")
    print(f"z={cartesian_coords.z}")


if __name__ == "__main__":
    main()
