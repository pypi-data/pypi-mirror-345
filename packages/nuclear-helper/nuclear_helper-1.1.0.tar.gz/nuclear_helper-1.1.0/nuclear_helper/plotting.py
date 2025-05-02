import matplotlib.pyplot as plt
import numpy as np

def plot_tetrahedron(vertices, hotspots):
    # Extract x, y, z coordinates from vertices
    xs = [vertex[0] for vertex in vertices]
    ys = [vertex[1] for vertex in vertices]
    zs = [vertex[2] for vertex in vertices]

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the vertices of the tetrahedron
    ax.scatter(xs, ys, zs, c='r', marker='o', label='3D Vertices')

    # Define the edges connecting the vertices
    edges = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3)
    ]

    # Draw red lines connecting the vertices
    for start, end in edges:
        ax.plot([xs[start], xs[end]],
                [ys[start], ys[end]],
                [zs[start], zs[end]],
                c='r', alpha=0.1)

    # Plot the projections onto the z=0 plane
    ax.scatter(xs, ys, zs=0, c='grey', marker='o', label='2D Projections')
    ax.scatter(hotspots[:, 0], hotspots[:, 1], zs=0, c='grey', marker='x', label='Hotspots')

    # Draw grey dashed lines from each vertex to its projection
    for x, y, z in zip(xs, ys, zs):
        ax.plot([x, x], [y, y], [z, 0], c='grey', linestyle='dashed')

    # Add a shaded plane at z=0
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    X, Y = np.meshgrid(np.linspace(xlim[0], xlim[1], 2),
                       np.linspace(ylim[0], ylim[1], 2))
    Z = np.zeros_like(X)
    ax.plot_surface(X, Y, Z, alpha=0.2, color='lightgrey')

    # Set labels and limits
    ax.set_xlabel('X [fm]')
    ax.set_ylabel('Y [fm]')
    ax.set_zlabel('Z [fm]')


    # Add a legend
    ax.legend()
    plt.tight_layout()

    # Display the plot
    plt.savefig('tetrahedron.pdf')
    plt.show()

def plot_2D_nuclear_density(density, params):
    # Create a 2D plot
    limit = params['b_max']
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # if b_grid is in params, plot the 2D density on the b_grid and make up for the log-scale of the b_grid

    # Define the extent of the axes
    extent = [-limit, limit, -limit, limit]
    # Plot the density with the specified extent
    im = ax.imshow(density, cmap='BrBG', origin='lower', extent=extent)

    # Add a colorbar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('T(X,Y) [-]')

    # Set labels
    ax.set_xlabel('X [fm]')
    ax.set_ylabel('Y [fm]')
    plt.tight_layout()
    # Display the plot
    plt.savefig('nuclear_density.pdf')
    plt.show()
    plt.close()
