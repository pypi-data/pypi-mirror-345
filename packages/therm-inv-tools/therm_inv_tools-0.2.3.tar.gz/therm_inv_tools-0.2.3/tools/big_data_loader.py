import numpy as np
import os.path
import glob
def __init__(self):
    # dont think i need anything here
    
wp_dens_path = os.path.expanduser(os.path.join('~', 'Desktop','Octopus_inversion', 'tests', 'WP_1', 'density_files'))
data_dir = wp_dens_path
file_list = sorted(glob.glob(os.path.join(data_dir, "rho*.y=0,z=0")))
np.loadtxt(f for f in file_list)



