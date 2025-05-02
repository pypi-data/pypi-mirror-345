import numpy as np
from scipy.spatial.transform import Rotation as R


# * Generate four vectors pointing the edges of a tetrahedron with a fixed arm length
def generate_random_tetrahedron(params):
    sigma = params['tetrahedron_spread']
    # The tetrahedron has a fixed arm length
    # Distance between two vertices is np.sqrt(4*x_shift**2 + 4*x_shift**2) = 2*np.sqrt(2)*x_shift
    # That is why I need to divide the arm length by 2
    r = params['tetrahedron_length'] / (2. * np.sqrt(2))
    V0 = np.array([r, r, r])
    V1 = np.array([-r, -r, r])
    V2 = np.array([-r, r, -r])
    V3 = np.array([r, -r, -r])
    # distance between two edges is

    # List of vertices
    vertices = [V0, V1, V2, V3]

    # Move each vertex by a random amount given by a Gaussian distribution
    for vertex in vertices:
        vertex += np.random.normal(0., sigma, 3)

    return random_rotation_fixed(vertices)
    # return rotate_tetrahedron(theta, phi, vertices)

def random_rotation_fixed(original_vertices):
    # Step 2: Choose a random axis of rotation using uniform distribution
    phi = np.random.uniform(0, 2 * np.pi)  # Azimuthal angle
    cos_theta = np.random.uniform(-1, 1)  # Cosine of polar angle
    theta = np.arccos(cos_theta)  # Polar angle
    # Plotting debug
    # initial_unit_vector = np.array([0, 0, 1])
    # plot_3D_vertices(original_vertices, unit_vector=initial_unit_vector)

    # Define the rotation matrix for z-axis (theta)
    Rz = np.array([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi), np.cos(phi), 0],
        [0, 0, 1]
    ])

    # Define the rotation matrix for y-axis (phi)
    Ry = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

    # Combined rotation matrix
    rotation_matrix = np.dot(Rz, Ry)
    # rotation_matrix = np.dot(Ry, Rz)
    # Apply the rotation to the vertices
    vertices_rotated = []
    for i in range(len(original_vertices)):
        vertices_rotated.append(np.dot(rotation_matrix, original_vertices[i]))


    # Convert the new direction to Cartesian coordinates (unit vector)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    axis = np.array([x, y, z])

    # Plotting debug
    # plot_3D_vertices(vertices_rotated, unit_vector=axis)

    # Step 3: Choose a random angle between 0 and 2pi
    angle = np.random.uniform(0, 2 * np.pi)

    # Step 4: Create the rotation object
    rotation = R.from_rotvec(axis * angle)

    # Step 5: Apply the rotation to the rotated vertices
    final_vertices = []
    for i in range(len(vertices_rotated)):
        rotated_vector = rotation.apply(vertices_rotated[i])
        final_vertices.append(rotated_vector)

    # Plotting debug
    # plot_3D_vertices(final_vertices, unit_vector=axis)

    return final_vertices


def make_2D_projection(vertices, axis=2):
    # drop the z-coordinate
    vertices_2D = []
    for vertex in vertices:
        # drop the axis-coordinates
        vertex_2D = np.delete(vertex, axis)
        vertices_2D.append(vertex_2D)
    return vertices_2D


if __name__ == '__main__':
    def plot_2D_vertices(vertices):
        bs_in_1d = np.linspace(-6., 6., 200)
        map_of_2d_vertices = np.zeros((200, 200))
        for i in range(len(vertices)):
            x = vertices[i][0]
            y = vertices[i][1]
            # find the closest point in the grid
            x_index = np.argmin(np.abs(bs_in_1d - x))
            y_index = np.argmin(np.abs(bs_in_1d - y))
            map_of_2d_vertices[x_index, y_index] += 1
        import matplotlib.pyplot as plt
        density_init = map_of_2d_vertices / np.max(map_of_2d_vertices)
        plt.imshow(0.1 * density_init / np.max(density_init), cmap='hot', vmax=0.1, vmin=-0.1)
        plt.colorbar()
        plt.xlabel('b_x [GeV^-1]')
        plt.ylabel('b_y [GeV^-1]')
        plt.show()
        plt.close()

    def plot_3D_vertices(vertices, unit_vector):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        vertices = np.array(vertices)
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2])
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        # plot the unit vector in the center of the tetrahedron
        ax.quiver(0, 0, 0, unit_vector[0], unit_vector[1], unit_vector[2], length=3.5, color='r', arrow_length_ratio=0.1)
        # set the limits of the axes
        ax.set_xlim([-3, 3])
        ax.set_ylim([-3, 3])
        ax.set_zlim([-3, 3])
        plt.show()
        plt.close()


    r = 3.42 / (2. * np.sqrt(2))
    V0 = np.array([r, r, r])
    V1 = np.array([-r, -r, r])
    V2 = np.array([-r, r, -r])
    V3 = np.array([r, -r, -r])
    vertices_initial = [V0, V1, V2, V3]

    vertices = []
    random_rotation_fixed(vertices_initial)
    for rotation in range(100000):
        vertices.append(random_rotation_fixed(vertices_initial))
    vertices = [item for sublist in vertices for item in sublist]
    for axis in range(3):
        plot_2D_vertices(make_2D_projection(vertices, axis=axis))
