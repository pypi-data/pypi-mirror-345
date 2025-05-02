import numpy as np

def make_b_grid(n_of_bs, b_max, b_grid=None):
    # Make the grid of bs as 2D vectors going on the square of size 2*b_max
    if b_grid is not None:
        bs_in_one_direction = b_grid
    else:
        bs_in_one_direction = one_direction(n_of_bs, b_max)
    bs = np.zeros((n_of_bs, n_of_bs, 2))
    for i in range(n_of_bs):
        for j in range(n_of_bs):
            bs[i, j, 0] = bs_in_one_direction[i]
            bs[i, j, 1] = bs_in_one_direction[j]
    return bs

def one_direction(n_of_bs, b_max):
    return np.linspace(-b_max, b_max, n_of_bs)

