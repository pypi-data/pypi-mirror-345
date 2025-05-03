import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def tetrahedron_to_hexahedra(vertices):
    """
    Convert a tetrahedral element defined by four vertices into four
    hexahedral elements.

    Parameters:
    vertices (np.ndarray): A 4x3 array containing the coordinates of the
    tetrahedron vertices.

    Returns:
    hexahedra (list): A list of four hexahedra, each defined by eight vertices.
    """
    # Ensure the input is a numpy array
    vertices = np.array(vertices)

    # Check if we have exactly 4 vertices
    if vertices.shape != (4, 3):
        raise ValueError("Input must be a 4x3 array of vertices.")

    # Extract the vertices
    A, B, C, D = vertices

    # Define the hexahedra vertices
    hexahedra = []

    # Each hexahedron is formed by adding the midpoints of the tetrahedron
    # edges
    mid_AB = (A + B) / 2
    mid_AC = (A + C) / 2
    mid_AD = (A + D) / 2
    mid_BC = (B + C) / 2
    mid_BD = (B + D) / 2
    mid_CD = (C + D) / 2

    # Define the four hexahedra
    hexahedra.append([A, mid_AB, mid_AC, mid_AD, mid_BC, B, mid_BD, mid_CD])
    hexahedra.append([B, mid_AB, mid_BC, mid_BD, mid_AC, A, mid_AD, mid_CD])
    hexahedra.append([C, mid_AC, mid_BC, mid_CD, mid_AB, A, mid_AD, mid_BD])
    hexahedra.append([D, mid_AD, mid_BD, mid_CD, mid_AB, A, mid_AC, mid_BC])

    return hexahedra


# Example usage
tetra_vertices = np.array(
    [
        [0, 0, 0],  # Vertex A
        [1, 0, 0],  # Vertex B
        [0, 1, 0],  # Vertex C
        [0, 0, 1],  # Vertex D
    ]
)

hexahedra = tetrahedron_to_hexahedra(tetra_vertices)

# Print the hexahedra vertices
for i, hexa in enumerate(hexahedra):
    print(f"Hexahedron {i + 1}:")
    for vertex in hexa:
        print(vertex)


def plot_tetrahedron_and_hexahedra(tetra_vertices, hexahedra):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Plot the tetrahedron
    tetra_faces = [
        [tetra_vertices[j] for j in [0, 1, 2]],
        [tetra_vertices[j] for j in [0, 1, 3]],
        [tetra_vertices[j] for j in [0, 2, 3]],
        [tetra_vertices[j] for j in [1, 2, 3]],
    ]

    ax.add_collection3d(
        Poly3DCollection(
            tetra_faces,
            facecolors="cyan",
            linewidths=1,
            edgecolors="r",
            alpha=0.25,
        )
    )

    # Plot the hexahedra
    for hexa in hexahedra:
        hexa_faces = [
            [hexa[j] for j in [0, 1, 2, 3]],
            [hexa[j] for j in [4, 5, 6, 7]],
            [hexa[j] for j in [0, 1, 5, 4]],
            [hexa[j] for j in [2, 3, 7, 6]],
            [hexa[j] for j in [0, 3, 7, 4]],
            [hexa[j] for j in [1, 2, 6, 5]],
        ]

        ax.add_collection3d(
            Poly3DCollection(
                hexa_faces,
                facecolors="orange",
                linewidths=1,
                edgecolors="b",
                alpha=0.5,
            )
        )

    # Set limits and labels
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Tetrahedron and Converted Hexahedra")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_zlim([0, 1])
    ax.view_init(elev=20, azim=30)

    plt.show()


# Example tetrahedron vertices
tetra_vertices = np.array(
    [
        [0, 0, 0],  # Vertex A
        [1, 0, 0],  # Vertex B
        [0, 1, 0],  # Vertex C
        [0, 0, 1],  # Vertex D
    ]
)

# Convert tetrahedron to hexahedra
hexahedra = tetrahedron_to_hexahedra(tetra_vertices)

# Plot the tetrahedron and hexahedra
plot_tetrahedron_and_hexahedra(tetra_vertices, hexahedra)
