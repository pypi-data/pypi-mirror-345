import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from scipy.optimize import curve_fit
from nuclear_helper.const_oxygen import parameters_de_Vries, gamma


def nuclear_profile(bs, c1, c2, c3, c4, c5):
    return c1 * np.exp(-c2 * bs**2) + c3 * np.exp(-c4 * bs ** c5)



def single_gaussian(r, R, Q, gamma):
    # I do not care about Ze, since that is just a constant
    A = Q/(2. * np.pi**(3./2.) * gamma**3 * (1 + 2 * R**2/gamma**2))
    return A * (np.exp(-((r - R)/gamma)**2) + np.exp(-((r + R)/gamma)**2))


def de_Vries_radial_profile(r):
    profile = np.zeros_like(r)
    for key in parameters_de_Vries:
        p = parameters_de_Vries[key]
        profile += single_gaussian(r, p['R'], p['Q'], gamma)
    return profile

# TODO: In case this gets too slow, I can precompute and parametrize this function
def integrated_deVries_over_z(bs):
    zs = np.linspace(0., 15., 1000)
    ws_over_b = []
    for b in bs:
        r_integrand = np.sqrt(b**2 + zs**2)
        ws = de_Vries_radial_profile(r_integrand)
        # integrate over z
        w_fixed_b = simps(ws, zs)
        ws_over_b.append(w_fixed_b)
    return np.array(ws_over_b)


def plot_comparison(bs):
    integrated_ws = integrated_deVries_over_z(bs)
    # normalize
    integrated_ws = integrated_ws / simps(integrated_ws, bs)
    plt.plot(bs, integrated_ws, label='integrated de Vries')

    popt = fit_integrated_woods_saxon(bs, integrated_ws)
    print('popt', popt)
    fitted = nuclear_profile(bs, popt[0], popt[1], popt[2], popt[3], popt[4])
    # fitted = fitted / simps(fitted, bs)
    plt.plot(bs, fitted, label='fitted')

    plt.title('Nuclear profile forde Vries $^4$He')

    plt.xlabel('b [fm]')
    plt.ylabel('probability density')

    plt.legend()
    # x-axis in log
    # plt.xscale('log')
    plt.show()
    plt.close()


def fit_integrated_woods_saxon(bs, integrated_ws):
    popt, pcov = curve_fit(nuclear_profile, bs, integrated_ws, maxfev=50000)
    return popt



if __name__ == '__main__':
    bs = np.logspace(-2., 1., 100)
    # bs = np.linspace(0., 10., 100)
    plot_comparison(bs)



