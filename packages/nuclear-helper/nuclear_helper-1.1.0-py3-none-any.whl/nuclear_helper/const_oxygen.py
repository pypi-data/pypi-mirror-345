import numpy as np

# Parameters for the de Vries profile for the alpha particle
RP = 1. # [fm]
gamma = RP * np.sqrt(2./3.)
# rms = 1.676 [fm]
parameters_de_Vries = {
                        '1': {'R': 0.2, 'Q': 0.034724},
                        '2': {'R': 0.6, 'Q': 0.430761},
                        '3': {'R': 0.9, 'Q': 0.203166},
                        '4': {'R': 1.4, 'Q': 0.192986},
                        '5': {'R': 1.9, 'Q': 0.083866},
                        '6': {'R': 2.3, 'Q': 0.033007},
                        '7': {'R': 2.6, 'Q': 0.014201},
                        '8': {'R': 3.1, 'Q': 0.000000},
                        '9': {'R': 3.5, 'Q': 0.006860},
                        '10': {'R': 4.2, 'Q': 0.000000},
                        '11': {'R': 4.9, 'Q': 0.000438},
                        '12': {'R': 5.2, 'Q': 0.000000}
                        }

fitted_parameters_for_integrated_deVries = [0.34612513, 0.40327957, 0.44270309, 0.44577645, 2.79883639]

# Hotspot number determination
p0 = 0.011
p0_hatta = 0.015
p1 = -0.58
p2 = 300.


