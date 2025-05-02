import numpy as np
from nuclear_helper.plotting import plot_tetrahedron, plot_2D_nuclear_density
from nuclear_helper.tetrahedron_geometry import generate_random_tetrahedron, make_2D_projection
from nuclear_helper.alpha_particle_generation import get_alpha_particle_hotspot_positions
from nuclear_helper.grid_oxygen import make_b_grid, one_direction
from scipy.integrate import simpson as simps


def hotspot_profile(distances, params):
    # Calculate the hotspot profile
    Bhs = params['Bhs']
    # Convert Bhs to fm^2
    Bhs = Bhs * 0.19732697**2
    return np.exp(-distances**2/(2.*Bhs))/(2.*np.pi*Bhs)

def get_hotspot_centers(x, params):
    # Do the calculations
    vertices_rotated = generate_random_tetrahedron(params)
    vertices_2D = make_2D_projection(vertices_rotated)

    hotspots = []
    for vertex in vertices_2D:
        hotspots.append(get_alpha_particle_hotspot_positions(x, vertex))
    # convert hotspots to a 2D array merging the subarrays
    hotspots = np.concatenate(hotspots)

    return hotspots, vertices_2D, vertices_rotated

def generate_oxygen_hotspot_density(x, params):
    # Initialize the grid of b vectors
    grid_of_b_vecs = make_b_grid(params['n_of_bs'], params['b_max'], params.get('b_grid', None))

    # Get the hotspot centers
    hotspots, vertices_2D, vertices_3D = get_hotspot_centers(x, params)

    distances = np.linalg.norm(grid_of_b_vecs - hotspots[:, np.newaxis, np.newaxis, :], axis=3)
    stacked_hotspot_profiles = (hotspot_profile(distances, params).T).T
    if params['de_Vries_helium']:
        from const_oxygen import fitted_parameters_for_integrated_deVries as popt
        from get_parametrization_for_integrated_deVries import nuclear_profile
        oxygen = np.zeros((params['n_of_bs'], params['n_of_bs']))
        for vertice in vertices_2D:
            distances = np.linalg.norm(grid_of_b_vecs - vertice, axis=2)
            oxygen += nuclear_profile(distances, popt[0], popt[1], popt[2], popt[3], popt[4])
        return oxygen, hotspots, vertices_2D, vertices_3D
    return np.sum(stacked_hotspot_profiles, axis=0), hotspots, vertices_2D, vertices_3D


def get_density(n_of_bs=200, b_max=6., tetrahedron_length=3.42, tetrahedron_spread=0.1, Bhs=0.8, x=0.01, seed=None, plot=False, positions=False, b_grid=None, de_Vries_helium=False):
    params = {
        'n_of_bs': n_of_bs,
        'b_max': b_max,  # fm
        'tetrahedron_length': tetrahedron_length,  # [fm]
        'tetrahedron_spread': tetrahedron_spread,  # [fm] gaussian sigma
        # Hotspot parameters
        'Bhs': Bhs,  # GeV^-2
        'b_grid': b_grid,
        'de_Vries_helium': de_Vries_helium
    }

    if b_grid is not None:
        params['n_of_bs'] = len(b_grid)

    if seed is not None:
        np.random.seed(seed)

    density, hotspots, vertices_2D, vertices_3D = generate_oxygen_hotspot_density(x, params)
    # normalize the density to one
    if b_grid is None:
        single_axis = one_direction(params['n_of_bs'], params['b_max'])
    else:
        single_axis = b_grid
    integral = simps(simps(density, x=single_axis), x=single_axis)
    density = density / integral
    # Plot the 3D density
    if plot:
        plot_tetrahedron(vertices_3D, hotspots)
        plot_2D_nuclear_density(density, params)

    if positions:
        return hotspots, vertices_2D, vertices_3D
    else:
        return single_axis, density


if __name__ == '__main__':
    # params = {
    #     'n_of_bs': 200,
    #     'b_max': 6.,  # fm
    #     'tetrahedron_length': 3.42,  # [fm]
    #     'tetrahedron_spread': 0.1,  # [fm] gaussian sigma
    #     # Hotspot parameters
    #     'Bhs': 0.8,  # GeV^-2
    #     'b_grid': None,
    #     'de_Vries_helium': False
    # }
    # # single_axis, density_init = get_density(x=0.01, plot=False, de_Vries_helium=False)
    # x=0.01
    # bs_in_1d = np.linspace(-params['b_max'], params['b_max'], params['n_of_bs'])
    # map_of_2d_vertices = np.zeros((params['n_of_bs'], params['n_of_bs']))
    # for event in range(10000):
    #     if event%100==0: print(event)
    #     # density, hotspots, vertices_2D, vertices_3D = generate_oxygen_hotspot_density(x, params)
    #     vertices_rotated = generate_random_tetrahedron(params)
    #     vertices_2D = make_2D_projection(vertices_rotated)
    #     # find the closest point in the grid for the x and y coordinates
    #     for i in range(len(vertices_2D)):
    #         x = vertices_2D[i][0]
    #         y = vertices_2D[i][1]
    #         # find the closest point in the grid
    #         x_index = np.argmin(np.abs(bs_in_1d - x))
    #         y_index = np.argmin(np.abs(bs_in_1d - y))
    #         map_of_2d_vertices[x_index, y_index] += 1
    #
    #     # single_axis, density = get_density(x=0.01, plot=False, de_Vries_helium=False)
    #     # density_init += density
    # import matplotlib.pyplot as plt
    #
    # density_init = map_of_2d_vertices / np.max(map_of_2d_vertices)
    # plt.imshow(0.1 * density_init / np.max(density_init), cmap='hot', vmax=0.1, vmin=-0.1)
    # plt.colorbar()
    # plt.title('Position of He vertices projected on the transverse plane')
    # plt.xlabel('b_x [GeV^-1]')
    # plt.ylabel('b_y [GeV^-1]')
    # plt.show()
    # plt.close()

    # plt.imshow(0.1 * density_init / np.max(density_init) - 0.1 * density_init.T / np.max(density_init), cmap='hot', vmax=0.02, vmin=-0.02)
    # plt.colorbar()
    # plt.title('Difference of the density x= 0.01')
    # plt.xlabel('b_x [GeV^-1]')
    # plt.ylabel('b_y [GeV^-1]')
    # plt.show()
    # plt.close()



    matej_grid = np.loadtxt('../tests_and_misc/matej_grid.txt')

    matej_grid *= 0.19732697
    # Make the grid from negative to positive values by flipping it
    # matej_grid = np.concatenate((-matej_grid[::-1], matej_grid))
    # print(matej_grid)
    index = 0
    single_axis, density_init = get_density(x=0.01, b_grid=matej_grid, plot=False, de_Vries_helium=True)
    while True:
        print(index)
        single_axis, density = get_density(x=0.01, b_grid=matej_grid, plot=False, de_Vries_helium=True)
        density_init = density_init + density
        if index % 100 == 0:
            plot_2D_nuclear_density(density_init/np.max(density_init), params={'b_max': 6.})
            np.savetxt(f'../tests_and_misc/oxygen_density_{index}.txt', density_init[0] / np.max(density_init[0]))
        index += 1



