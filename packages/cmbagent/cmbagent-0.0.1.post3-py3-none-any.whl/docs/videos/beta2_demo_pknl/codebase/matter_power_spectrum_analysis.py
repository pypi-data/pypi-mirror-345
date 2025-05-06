# filename: codebase/matter_power_spectrum_analysis.py
#!/usr/bin/env python3
"""
This script computes the linear and non-linear matter power spectra using classy_sz,
analyzes the transition from linear to non-linear regimes by examining the ratio
P_{NL}(k,z) / P_{L}(k,z), and creates visualizations (a contour plot and a transition plot)
that display where non-linear effects become significant. All results are saved in the
data/ folder.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Enable LaTeX rendering and set font properties for plots
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'

from classy_sz import Class as Class_sz

def compute_power_spectra_for_zes(classy_sz, z_list, cosmo_params):
    r"""
    Compute the linear and non-linear matter power spectra for a range of redshifts and
    return the interpolated ratio on a common k-grid.

    Args:
        classy_sz: Instance of the classy_sz Class.
        z_list (array-like): Array of redshift values at which to compute the power spectra.
        cosmo_params (dict): Dictionary of cosmological parameters.

    Returns:
        common_k (numpy.ndarray): 1D array of common k values (in h/Mpc) for all redshifts.
        ratio_2d (numpy.ndarray): 2D array of power spectrum ratios with shape (n_z, n_k).
        z_list (numpy.ndarray): Array of redshift values corresponding to the rows of ratio_2d.
    """
    ratio_list = []
    k_arrays = []
    
    for z in z_list:
        # Compute linear power spectrum at redshift z
        pks_linear, ks_linear = classy_sz.get_pkl_at_z(z, params_values_dict=cosmo_params)
        # Compute non-linear power spectrum at redshift z
        pks_nonlinear, ks_nl = classy_sz.get_pknl_at_z(z, params_values_dict=cosmo_params)
        # Use the linear k-array; assume ks_linear and ks_nl are similar
        ratio = pks_nonlinear / pks_linear
        ratio_list.append(ratio)
        k_arrays.append(ks_linear)
    
    # Determine the common k-range from all redshifts
    common_k_min = max(ks[0] for ks in k_arrays)
    common_k_max = min(ks[-1] for ks in k_arrays)
    N_k = 1000
    common_k = np.linspace(common_k_min, common_k_max, N_k)
    
    # Interpolate each ratio array onto the common k grid
    ratio_2d = np.zeros((len(z_list), N_k))
    for i, (z, ratio, ks_current) in enumerate(zip(z_list, ratio_list, k_arrays)):
        ratio_interp = np.interp(common_k, ks_current, ratio)
        ratio_2d[i, :] = ratio_interp
    
    return common_k, ratio_2d, z_list

def compute_transition_k(common_k, ratio_2d, threshold):
    r"""
    Compute the transition wavenumber for each redshift at which the non-linear effects
    become significant (i.e., where the ratio P_{NL}/P_{L} exceeds the threshold).

    Args:
        common_k (numpy.ndarray): 1D array of common k values.
        ratio_2d (numpy.ndarray): 2D array (n_z x n_k) of power spectrum ratios.
        threshold (float): Threshold value to define a significant non-linear effect.

    Returns:
        transition_k (numpy.ndarray): 1D array of transition k values for each redshift.
            If the ratio never exceeds the threshold at a given redshift, np.nan is assigned.
    """
    n_z = ratio_2d.shape[0]
    transition_k = np.empty(n_z)
    
    for i in range(n_z):
        row = ratio_2d[i, :]
        if np.all(row < threshold):
            transition_k[i] = np.nan
        else:
            idx = np.argmax(row >= threshold)
            if idx == 0:
                transition_k[i] = common_k[0]
            else:
                # Linear interpolation between the two adjacent k values
                k1, k2 = common_k[idx-1], common_k[idx]
                r1, r2 = row[idx-1], row[idx]
                transition_k[i] = k1 + (threshold - r1) / (r2 - r1) * (k2 - k1)
    
    return transition_k

def plot_contour(common_k, ratio_2d, z_list, transition_k, threshold, output_file):
    r"""
    Create a contour plot of the power spectrum ratio in the k-z plane and overlay the
    transition points where the ratio exceeds the threshold.

    Args:
        common_k (numpy.ndarray): 1D array of k values.
        ratio_2d (numpy.ndarray): 2D array of power spectrum ratios with shape (n_z, n_k).
        z_list (numpy.ndarray): Array of redshift values corresponding to rows of ratio_2d.
        transition_k (numpy.ndarray): Array of transition k values for each redshift.
        threshold (float): Threshold value for significant non-linear effects.
        output_file (str): Path to save the generated plot.
    """
    plt.figure(figsize=(8,6))
    X, Y = np.meshgrid(common_k, z_list)
    cp = plt.contourf(X, Y, ratio_2d, levels=50, cmap='viridis')
    plt.colorbar(cp, label=r'$\frac{P_{NL}(k,z)}{P_{L}(k,z)}$')
    plt.xlabel(r'$k \, [h/{\rm Mpc}]$')
    plt.ylabel('Redshift $z$')
    plt.title('Ratio of Non-linear to Linear Matter Power Spectrum')
    
    # Overlay the contour line at the threshold value
    cs = plt.contour(X, Y, ratio_2d, levels=[threshold], colors='red', linestyles='--')
    plt.clabel(cs, fmt='%1.2f', colors='red')
    # Overlay transition points
    plt.scatter(transition_k, z_list, color='white', edgecolor='black', label='Transition $k$')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def plot_transition_k_vs_z(z_list, transition_k, threshold, output_file):
    r"""
    Create a plot of the transition wavenumber versus redshift.

    Args:
        z_list (numpy.ndarray): Array of redshift values.
        transition_k (numpy.ndarray): Array of transition k values for each redshift.
        threshold (float): Threshold value used in determining transition k.
        output_file (str): Path to save the generated plot.
    """
    plt.figure(figsize=(8,6))
    plt.plot(z_list, transition_k, marker='o', color='blue',
             label=r'Transition $k$ (threshold = %.2f)' % threshold)
    plt.xlabel('Redshift $z$')
    plt.ylabel(r'Transition $k \, [h/{\rm Mpc}]$')
    plt.title('Transition Scale $k$ vs Redshift')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def main():
    r"""
    Main function to initialize classy_sz, compute the linear and non-linear matter power spectra
    over a range of redshifts, determine the transition scale where non-linear effects become significant,
    create visualizations, and save the results.
    """
    # Create directory for saving results
    os.makedirs('data', exist_ok=True)
    
    # Initialize classy_sz and set required options
    classy_sz = Class_sz()
    classy_sz.set({'output': 'mPk'})  # Request the matter power spectrum
    classy_sz.initialize_classy_szfast()
    
    # Define the cosmological parameters
    cosmo_params = {
        'omega_b': 0.02242,
        'omega_cdm': 0.11933,
        'H0': 67.66,
        'tau_reio': 0.0561,
        'ln10^{10}A_s': 3.047,
        'n_s': 0.9665,
    }
    
    # Define a range of redshifts for the analysis (from z = 0 to z = 2)
    z_list = np.linspace(0, 2, 11)  # 11 points: 0, 0.2, ..., 2.0
    
    # Compute the power spectra and the ratio for each redshift
    common_k, ratio_2d, z_list = compute_power_spectra_for_zes(classy_sz, z_list, cosmo_params)
    
    # Define the threshold for significant non-linear effects (e.g., 5% deviation)
    threshold = 1.05
    
    # Compute the transition k for each redshift where the ratio exceeds the threshold
    transition_k = compute_transition_k(common_k, ratio_2d, threshold)
    
    # Create and save a contour plot of the power spectrum ratio in the k-z plane
    contour_plot_file = 'data/matter_power_spectrum_transition_contour.png'
    plot_contour(common_k, ratio_2d, z_list, transition_k, threshold, contour_plot_file)
    
    # Create and save a plot of the transition k versus redshift
    transition_plot_file = 'data/transition_k_vs_z.png'
    plot_transition_k_vs_z(z_list, transition_k, threshold, transition_plot_file)
    
    # Save the transition data to a CSV file for further analysis
    csv_file = 'data/transition_k_vs_z.csv'
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['z', 'transition_k'])
        for z, k_val in zip(z_list, transition_k):
            writer.writerow([z, k_val])
    
    print("Computation complete. Results and plots saved in the data/ folder.")

if __name__ == '__main__':
    main()
