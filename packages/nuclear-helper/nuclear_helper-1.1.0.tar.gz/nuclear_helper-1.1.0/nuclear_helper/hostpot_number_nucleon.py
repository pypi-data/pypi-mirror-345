import numpy as np
from . import const_oxygen as c

def get_number_of_hotspots_real(x):
    return c.p0 * x ** c.p1 * (1. + c.p2 * np.sqrt(x))


def zero_trunckated_poisson_distribution(mu):
    l = 1
    t = mu * np.exp(-mu)/(1. - np.exp(-mu))
    s = t

    u = np.random.uniform()
    while s < u:
        l += 1
        t *= mu / l
        s += t
    return l


def get_number_of_hotspots(x):
    return zero_trunckated_poisson_distribution(get_number_of_hotspots_real(x))

