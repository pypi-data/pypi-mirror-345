# filename: codebase/generate_datasets.py
import numpy as np
import os
from classy_sz import Class as Class_sz

def sample_cosmo_params():
    r"""
    Sample cosmological parameters uniformly from predefined ranges.
    
    Returns:
        dict: A dictionary containing sampled values for:
            - 'omega_b': Baryon density parameter
            - 'omega_cdm': Cold dark matter density parameter
            - 'H0': Hubble constant
            - 'tau_reio': Optical depth to reionization
            - 'ln10^{10}A_s': Log amplitude of the primordial scalar fluctuations
            - 'n_s': Scalar spectral index
    """
    return {
        'omega_b': np.random.uniform(0.020, 0.024),
        'omega_cdm': np.random.uniform(0.107, 0.131),
        'H0': np.random.uniform(60, 75),
        'tau_reio': np.random.uniform(0.04, 0.07),
        'ln10^{10}A_s': np.random.uniform(2.9, 3.2),
        'n_s': np.random.uniform(0.94, 1.0)
    }

def get_params_vector(cosmo_params):
    r"""
    Convert a dictionary of cosmological parameters to a vector following a fixed order.
    
    Args:
        cosmo_params (dict): Dictionary of cosmological parameters.
    
    Returns:
        np.ndarray: 1D array of parameter values in the order:
                    ['omega_b', 'omega_cdm', 'H0', 'tau_reio', 'ln10^{10}A_s', 'n_s']
    """
    order = ['omega_b', 'omega_cdm', 'H0', 'tau_reio', 'ln10^{10}A_s', 'n_s']
    return np.array([cosmo_params[key] for key in order])

def generate_sample(classy_sz_instance):
    r"""
    Generate one sample of the linear matter power spectrum using random cosmological parameters and redshift.
    
    Args:
        classy_sz_instance (Class_sz): An initialized instance of the classy_sz package.
    
    Returns:
        tuple: A tuple containing:
            - params_vector (np.ndarray): Array of sampled cosmological parameters in fixed order.
            - z (float): Sampled redshift value.
            - log_pks (np.ndarray): Natural logarithm of the computed linear matter power spectrum.
            - ks (np.ndarray): Wavenumber values corresponding to the power spectrum.
    """
    cosmo_params = sample_cosmo_params()
    # Sample redshift uniformly from 0.1 to 1.0
    z = np.random.uniform(0.1, 1.0)
    pks, ks = classy_sz_instance.get_pkl_at_z(z, params_values_dict=cosmo_params)
    log_pks = np.log(pks)
    params_vector = get_params_vector(cosmo_params)
    return params_vector, z, log_pks, ks

def main():
    r"""
    Main function to generate and save training and testing datasets for the linear matter power spectrum.
    
    The function performs the following steps:
        1. Creates a 'data/' directory if it does not exist.
        2. Initializes a single instance of the classy_sz package.
        3. Generates 500 training samples and 50 testing samples by sampling the cosmological parameter space and redshift.
        4. Stores the natural logarithm of the computed power spectra (log(P(k))) along with the parameters and redshifts.
        5. Saves the datasets in NPZ format in the 'data/' directory.
    """
    # Create the data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Initialize classy_sz instance once (all initialization steps outside of loops)
    classy_sz_instance = Class_sz()
    classy_sz_instance.set({'output': 'mPk'})
    classy_sz_instance.initialize_classy_szfast()  # Critical initialization
    
    # Define number of training and testing samples
    n_train = 500
    n_test = 50
    
    # Lists for training data
    train_params = []  # List of parameter vectors
    train_zs = []      # List of redshift values
    train_log_pks = [] # List of log(P(k)) arrays
    
    # Lists for testing data
    test_params = []
    test_zs = []
    test_log_pks = []
    
    # Generate first sample to obtain the k grid
    sample_params, sample_z, sample_log_pks, ks = generate_sample(classy_sz_instance)
    train_params.append(sample_params)
    train_zs.append(sample_z)
    train_log_pks.append(sample_log_pks)
    
    # Generate remaining training samples
    for i in range(n_train - 1):
        params_vector, z, log_pks, ks_i = generate_sample(classy_sz_instance)
        train_params.append(params_vector)
        train_zs.append(z)
        train_log_pks.append(log_pks)
        
        # Check that k values are consistent across samples
        if not np.allclose(ks, ks_i, atol=1e-6):
            print("Warning: k values differ between samples in training set!")
    
    # Generate testing samples
    for i in range(n_test):
        params_vector, z, log_pks, ks_i = generate_sample(classy_sz_instance)
        test_params.append(params_vector)
        test_zs.append(z)
        test_log_pks.append(log_pks)
        if not np.allclose(ks, ks_i, atol=1e-6):
            print("Warning: k values differ between samples in testing set!")
    
    # Convert lists to numpy arrays
    train_params = np.array(train_params)  # Shape: (n_train, 6)
    train_zs = np.array(train_zs)          # Shape: (n_train,)
    train_log_pks = np.array(train_log_pks)  # Shape: (n_train, num_k)
    test_params = np.array(test_params)      # Shape: (n_test, 6)
    test_zs = np.array(test_zs)              # Shape: (n_test,)
    test_log_pks = np.array(test_log_pks)      # Shape: (n_test, num_k)
    
    # Save the datasets to the data directory in npz format
    np.savez(os.path.join(data_dir, 'training_dataset.npz'),
             params=train_params, zs=train_zs, log_pks=train_log_pks, ks=ks)
    np.savez(os.path.join(data_dir, 'testing_dataset.npz'),
             params=test_params, zs=test_zs, log_pks=test_log_pks, ks=ks)
    
    print("Training and testing datasets saved in the 'data/' directory.")

if __name__ == "__main__":
    main()
