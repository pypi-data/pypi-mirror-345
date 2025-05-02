import numpy as np
from .const_oxygen import fitted_parameters_for_integrated_deVries as popt
from .hostpot_number_nucleon import get_number_of_hotspots
from .get_parametrization_for_integrated_deVries import de_Vries_radial_profile, nuclear_profile


def get_hotspot_distances_for_alpha_particle(number_of_hotspots):
    while True:
        n_of_samples = 10000
        random_0_to_1 = np.random.uniform(0., 1., n_of_samples)

        # THIS DOES THE TRICK TO DISTRIBUTE POLAR RANDOM NUMBER UNIFORMLY
        random_0_to_1 = np.sqrt(random_0_to_1)
        random_rs = random_0_to_1 * 5.  # fm

        max_probability = nuclear_profile(0., popt[0], popt[1], popt[2], popt[3], popt[4])
        functional_values = nuclear_profile(random_rs, popt[0], popt[1], popt[2], popt[3], popt[4])
        random_ys = np.random.uniform(0., max_probability, n_of_samples)
        allowed_rs = random_rs[random_ys < functional_values]

        # pass only the first A of them
        if len(allowed_rs) > number_of_hotspots:
            return allowed_rs[:number_of_hotspots]


def get_hotspot_centers_for_alpha_particle(number_of_hotspots):
    distances = get_hotspot_distances_for_alpha_particle(number_of_hotspots)
    alpha_angles = np.random.uniform(0., 2. * np.pi, number_of_hotspots)
    # add them to a vector array
    alpha_positions = np.zeros((number_of_hotspots, 2))
    alpha_positions[:, 0] = distances * np.cos(alpha_angles)
    alpha_positions[:, 1] = distances * np.sin(alpha_angles)
    return alpha_positions


def get_number_of_hotspots_for_alpha_particle(x):
    number_of_hotspots = 0
    for i in range(4):
        number_of_hotspots += get_number_of_hotspots(x)
    return number_of_hotspots


def get_alpha_particle_hotspot_positions(x, center):
    number_of_hotspots = get_number_of_hotspots_for_alpha_particle(x)
    alpha_positions = get_hotspot_centers_for_alpha_particle(number_of_hotspots)
    return alpha_positions + center



if __name__=='__main__':
    import matplotlib.pyplot as plt
    # Plot the de Vries radial profile
    r = np.linspace(0., 4., 100)
    profile = de_Vries_radial_profile(r)
    plt.xlabel('r [fm]')
    plt.ylabel('probability density de Vries He [fm$^{-3}$]')
    plt.plot(r, profile)
    plt.show()
    # get the root mean square of the de Vries profile
    rms = np.sqrt(np.sum(r**4 * profile) / np.sum(profile))
    print('rms', rms)













