import numpy as np
import numpy as np
import scipy.sparse as spa
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
from scipy.integrate import simps
import matplotlib.animation as animation
from IPython.display import HTML
import iDEA
import math
from matplotlib import cm
import scipy
from decimal import Decimal
from matplotlib import animation, rc
# Code from V. Martinetto and Anthony R. Osborne 
# Modified for documentation and packaging purposes by Anthony R. Osborne

## External potential function
def v_atomic(Z, x):
    """
    INPUT: 
        Z: Integer, atomic number
        x: Array, grid to evaluate on
    """
    return -Z/(np.abs(x)+.5)
def v_diatomic(Z, x, d):
    """
    INPUT: 
        Z: Integer, atomic number
        x: Array, grid to evaluate on
    """
    return -Z/(abs(x + 0.5*d) + 1.0) -Z/(abs(x - 0.5*d) + 1.0)

## Occupation functions
### Spin String function
def occ_string(N):
    """
    Function to write an up/down spin string
    """
    occ_string = ''
    for i in range(N):
        i+=1
        if i%2==0:
            occ_string += 'd'
        else:
            occ_string += 'u'
    return occ_string

### Fermi Occupation function
def fermi_occs(Eis,mu,tau):
    '''
    INPUT:
        tau: Scalar the tau value to find the temprature dependent mu for
        mus: scalar a guess at a value below the chemical potential for tau
        Eis: Scalar Some kind of energy 
    OUTPUT
        F_occs: Scalar The Fermi Occupation for mu, tau, Eis
    '''
    F_occs = 1/(1+np.exp((Eis-mu)/tau))
    return F_occs

### Boltzmann Occupation Function
def boltz_occs(Eis,mu,T,N):
    '''
    INPUT:
        Eis: np.array, size=(nstates,N) The eigenvalues of the zero temprature interacting wavefunctions of the system. It is an nstates x N array.Enregy will increase moving down the matrix and number of particlea from left to right. position (0,0) will be the ernergy for the ground state of the one particle system.
        Mu: Scalar, float The temprature dependent chemical potnetial of the N-particle system.
        T: Scalar, float The temprature of the N-particle system in K.
        N: Integer The number of particles in the final thermal density.
    OUTPUT:
        w: np.array, size=(nstates,N) The boltzamn weights that result in the thermal density at chemical potnetial, mu, and temprature, T.
    '''
    
    kb = 3.166811563e-6 # Ha K^-1
    B = 1/(kb*T)
    nstates = np.shape(Eis)[0]
    
    #calculate the partition function and save the un-normalized boltzman weights. Only have to loop through N one time.
    partition = 0
    w = np.empty((nstates,N))
    for i in range(N):
        for j in range(nstates):
            w[j,i] = np.exp(-B*(Eis[j,i]-(mu*(i+1))))
            partition += w[j,i]
            
    #Normalize the boltzman weights
    w = w/partition
    
    return w, partition

## Root finding tools

### Secant -- used in Secant method for root finding
def secant(x0,x1,fx0,fx1):
    '''
    the update process for the secant method
    '''
    return (x0*fx1-fx0*x1)/(fx1-fx0)
### Secant method for root finding 
def secant_method(x0,x1,func,criterion=1e-6,max_iter=100):
    '''
    Description: Based on the secant method page on wikipedia
    takes the first two guesses at the correct root and a defined
    function then run the secant method to find the root.
    INPUT:
        x0: Scalar First guess at root value
        x1: scalar Second guess at root value
        func: Scalar Function to find root of
    OUTPUT
        x1: Scalar Root value
        fx1: Scalar function evaluated at root value            
    '''
    
    i = 0
    
    fx0 = func(x0)
    fx1 = func(x1)
    conv = abs(min([fx0,fx1]))
    
    while conv > criterion:
        xt = secant(x0,x1,fx0,fx1)
        
        fx0 = fx1
        x0 = x1
        x1 = xt
        fx1 = func(x1)
        
        conv = abs(fx1)
        
        if i > max_iter:
            break
        i += 1
        
    return x1,fx1
## Particle number tools

### Fermi weight functions

#### Functions to calculate density
def fermi_dens_function(fs,vecs,x):
    '''
    Description: 
    INPUT:
        fs: ndarray
            
        vecs: ndarray
            
        x: ndarray
            
    OUTPUT
        Dens: ndarray The density for the system
    '''
    dens = np.zeros(len(x))
    for i,f in enumerate(fs):
        dens+=2*f*vecs[:,i]**2
    return dens

#### Function to calculate number of particles for a given mu and tau (unshifted)
def fermi_particle_number_function(mu,tau,vals,vecs,x):
    '''
    Description: Determine the Unshifted particle number
    INPUT:
        mu: Scalar (float) chemical potential
        tau: Scalar (float) Electronic temperature
        vecs: ndarray Eigenvectors
        vals: ndarray Eigenvalues 
        x: ndarray Grid
    OUTPUT
        Ne: Scalar (float) The unshifted particle number
    '''
    fs = fermi_occs(vals,mu,tau)
    dens = np.zeros(len(x))
    for i,f in enumerate(fs):
        dens += 2*f*vecs[:,i]**2
    Ne = np.trapz(dens,x)
    return Ne

### Function to calculate number of particles for a given mu and tau (shifted)
def fermi_particle_number_shifter(tau,vals,vecs,x,target_Ne): 
    
    '''
    Old title: particle_number_function_function

    Description: Determines the Shifted particle number
    INPUT:
        tau: Scalar (float) Electronic temperature
        vecs: ndarray Eigenvectors
        vals: ndarray Eigenvalues 
        x: ndarray Grid
        target_Ne: Scalar (int) The desired particle number
    OUTPUT
        particle_number_Shift: Scalar (float) The Shifted particle number
    '''

    def fermi_particle_number_Shift(mu):
        
        fs = fermi_occs(vals,mu,tau)
        dens = np.zeros(len(x))
        for i,f in enumerate(fs):
            dens += 2*f*vecs[:,i]**2
        Ne = np.trapz(dens,x)
        
        return Ne - target_Ne

    return fermi_particle_number_Shift
### Boltzmann weight Functions

#### Functions to calculate density
def boltz_dens_function(vals,mu,tau,densities):
    '''
    Description: Determine the Unshifted particle number
    INPUT:
        mu: Scalar (float)
            chemical potential
        tau: Scalar (float)
            Electronic temperature
        vecs: ndarray
            Eigenvectors
        vals: ndarray
            Eigenvalues 
        x: ndarray
            Grid
    OUTPUT
        Ne: Scalar (float)
            The unshifted particle number
    '''
    
    nk = vals.shape[0]
    ne = vals.shape[1]
    nx = len(densities[0,:,0])
    
    kb = 3.166811563e-6 # Ha K^-1
    T = tau/kb
    
    w, partition = boltz_occs(vals,mu,T,ne)

    dens = np.zeros(nx)
    for i in range(ne):
        for j in range(nk):
            dens += w[j,i]*densities[i,:,j]
    return dens

#### Function to calculate number of particles for a given mu and tau 
def boltz_particle_number_function(mu,tau,vals,densities,ne,x):
    '''
    Description: Determine the Unshifted particle number
    INPUT:
        mu: Scalar (float)
            chemical potential
        tau: Scalar (float)
            Electronic temperature
        vecs: ndarray
            Eigenvectors
        vals: ndarray
            Eigenvalues 
        x: ndarray
            Grid
    OUTPUT
        Ne: Scalar (float)
            The unshifted particle number
    '''

    nx = len(x)
    nk = vals.shape[0]
    
    # convert temp in units of Ha into K
    kb = 3.166811563e-6 # Ha K^-1
    T = tau/kb

    # obtain boltzman weights 
    w, partition = boltz_occs(vals,mu,T,ne)
    dens = np.zeros(nx)
    for i in range(ne):
        for j in range(nk):
            dens += w[j,i]*densities[i,:,j]
    Ne = np.trapz(dens,x)
    return Ne

### Function to calculate number of particles for a given mu and tau (shifted)
def boltz_particle_number_shifter(tau,vals,densities,ne,x,target_ne):
    '''
    Description: Determine the Unshifted particle number
    INPUT:
        mu: Scalar (float)
            chemical potential
        tau: Scalar (float)
            Electronic temperature
        vecs: ndarray
            Eigenvectors
        vals: ndarray
            Eigenvalues 
        x: ndarray
            Grid
    OUTPUT
        Ne: Scalar (float)
            The unshifted particle number
    '''

    def boltz_particle_number_Shift(mu):
        
        nx = len(x)
        nk = vals.shape[0]
    
        # convert temp in units of Ha into K
        kb = 3.166811563e-6 # Ha K^-1
        T = tau/kb

        # obtain boltzman weights 
        w, partition = boltz_occs(vals,mu,T,ne)
        dens = np.zeros(nx)
        for i in range(ne):
            for j in range(nk):
                dens += w[j,i]*densities[i,:,j]
        Ne = np.trapz(dens,x)
        
        return Ne - target_ne
    
    return boltz_particle_number_Shift
## Chemical potential calculation functions

### Search function to search over a range of \tau that returns \mu for each \tau such that a number of particles is conserved
def tau_search(taus,mu0,mu1,vals,vecs,x,Ne,criterion=1e-10):
    '''
    INPUT:
        taus: vector, len=n
            the tau value to find the temperature dependent mu for
        mu0: scalar
            a guess at a value below the chemical potential for taus[0]
        mu1: scalar
            a guess for a value above the chemical potential for taus[0]
        vals: vector, len=k
            The eigenvalues of the eigenvectors that the mus should be computed for
        vecs: matrix, size=(Nx,k)
            The eigenvectors of the system that mu should be found for for each tau.
            Nx is the number of grid points.
            k is the number of states included in the calculation.
        x: vector, len=Nx
            The grid that the eigenvectors were computed on.
        Ne: scalar
            The fixed number of electrons in the system
        criterion: scalar
            The convergence criterion that the secant method should look to obtain
    OUTPUT
        mus: vector, len=n
            the chemical potnetial at each temp tau to conserve the number of particles in the system
    '''
    dtau = taus[1]-taus[0]
    mus = np.empty(len(taus))

    for i,tau in enumerate(taus):
        
        func = particle_number_shifter(tau,vals,vecs,x,Ne)
        mu1,fx0 = secant_method(mu0,mu1,func,criterion=criterion)
    
        mus[i] = mu1
    
        mu0 = mu1-(dtau+(.1*dtau*i))
        
    return mus
