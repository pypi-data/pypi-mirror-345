import numpy as np


def main():
    import sys
    import os
    from nuclear_helper.oxygen import get_density
    n_of_bs = 200
    b_max = 6.
    tetrahedron_length = 3.42
    tetrahedron_spread = 0.1
    Bhs = 0.8
    x = 0.01
    n_of_nuclei = 1
    seed = None
    plot = False
    positions = False

    for arg in sys.argv[1:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            if key == 'n_of_bs':
                n_of_bs = int(value)
            elif key == 'n_of_nuclei':
                n_of_nuclei = int(value)
            elif key == 'b_max':
                b_max = float(value)
            elif key == 'tetrahedron_length':
                tetrahedron_length = float(value)
            elif key == 'tetrahedron_spread':
                tetrahedron_spread = float(value)
            elif key == 'Bhs':
                Bhs = float(value)
            elif key == 'x':
                x = float(value)
            elif key == 'seed':
                seed = int(value)
            elif key == 'plot':
                plot = bool(value)
            elif key == 'positions':
                positions = bool(value)
            else:
                raise ValueError(f"Unknown parameter: {key}")
        else:
            raise ValueError(f"Unknown parameter: {arg}")
    if not os.path.isdir('data'):
        os.mkdir('data')
    for i in range(n_of_nuclei):
        if n_of_nuclei > 1:
            prefix = 'data/' + f'{i}_'
        else:
            prefix = 'data/'
        if positions:
            hotspots, vertices_2D, vertices_3D = get_density(n_of_bs, b_max, tetrahedron_length, tetrahedron_spread, Bhs, x, seed, plot, positions)
            np.savetxt(prefix + 'hotspots.txt', hotspots)
            np.savetxt(prefix + 'vertices_2D.txt', vertices_2D)
            np.savetxt(prefix + 'vertices_3D.txt', vertices_3D)
        else:
            single_axis, density = get_density(n_of_bs, b_max, tetrahedron_length, tetrahedron_spread, Bhs, x, seed, plot, positions)
            if i==0:
                np.savetxt('data/single_axis.txt', single_axis)
            np.savetxt(prefix + 'density.txt', density)


if __name__ == '__main__':
    main()

# To compile a new distribution, run the following command: pyinstaller --onedir main.py