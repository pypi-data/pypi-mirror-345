# filename: codebase/compare_architectures.py
import numpy as np
import os
import time
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Enable LaTeX rendering and set font properties for plotting
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'

def load_dataset(file_path):
    r"""
    Load dataset from an NPZ file.

    Args:
        file_path (str): Path to the NPZ file containing the dataset.

    Returns:
        tuple: Tuple containing arrays:
            - params (np.ndarray): Cosmological parameters (shape: [num_samples, 6])
            - zs (np.ndarray): Redshift values (shape: [num_samples,])
            - log_pks (np.ndarray): Natural logarithm of the power spectra (shape: [num_samples, num_k])
            - ks (np.ndarray): Wavenumber grid (shape: [num_k,])
    """
    data = np.load(file_path)
    params = data['params']
    zs = data['zs']
    log_pks = data['log_pks']
    ks = data['ks']
    return params, zs, log_pks, ks

def prepare_transformer_data(params, zs, log_pks, ks):
    r"""
    Prepare input features and targets for the transformer model.

    For each sample, a sequence of tokens is formed with length equal to the number
    of k values. Each token is constructed by concatenating the k value with the constant
    cosmological features (parameters and redshift) for that sample.

    Args:
        params (np.ndarray): Array of cosmological parameters (shape: [num_samples, 6]).
        zs (np.ndarray): Array of redshift values (shape: [num_samples,]).
        log_pks (np.ndarray): Array of log-transformed power spectra (shape: [num_samples, num_k]).
        ks (np.ndarray): Array of wavenumber values (shape: [num_k,]).

    Returns:
        tuple: (X_seq, Y_seq) where:
            - X_seq (np.ndarray): Input sequence for the transformer of shape (num_samples, num_k, 8),
                                  each token is [k, param1, ..., param6, z].
            - Y_seq (np.ndarray): Target sequence with shape (num_samples, num_k, 1).
    """
    n_samples = params.shape[0]
    num_k = ks.shape[0]
    X_base = np.concatenate([params, zs.reshape(-1, 1)], axis=1)  # shape: (n_samples, 7)
    X_base_rep = np.repeat(X_base[:, np.newaxis, :], num_k, axis=1)  # shape: (n_samples, num_k, 7)
    ks_rep = np.tile(ks.reshape(1, num_k, 1), (n_samples, 1, 1))      # shape: (n_samples, num_k, 1)
    X_seq = np.concatenate([ks_rep, X_base_rep], axis=2)              # shape: (n_samples, num_k, 8)
    Y_seq = log_pks[..., np.newaxis]                                  # shape: (n_samples, num_k, 1)
    return X_seq, Y_seq

def main():
    r"""
    Main function to compare the two neural network architectures (MLP and Transformer)
    for predicting the linear matter power spectrum. The script performs:
      1. Loading the testing dataset.
      2. Loading the trained models (using a custom_objects dictionary to resolve 'mse').
      3. Preparing proper inputs for each model.
      4. Benchmarking inference speed.
      5. Computing test MSE and maximum relative error.
      6. Plotting predicted vs true power spectra (on log scales).
      7. Determining and reporting the best architecture.
      8. Saving the plot to disk.
    """
    # Set seeds for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    data_dir = "data"
    test_file = os.path.join(data_dir, "testing_dataset.npz")
    test_params, test_zs, test_log_pks, ks = load_dataset(test_file)
    
    # Prepare input for MLP: concatenate cosmological parameters and redshift (shape: [num_samples, 7])
    X_test_mlp = np.concatenate([test_params, test_zs.reshape(-1, 1)], axis=1)
    
    # Specify custom_objects for model loading to resolve 'mse'
    # Using MeanSquaredError instance instead of tf.keras.losses.mean_squared_error
    custom_objects = {'mse': tf.keras.losses.MeanSquaredError()}
    mlp_model_path = os.path.join(data_dir, "mlp_model.h5")
    transformer_model_path = os.path.join(data_dir, "transformer_model.keras")
    mlp_model = tf.keras.models.load_model(mlp_model_path, custom_objects=custom_objects)
    transformer_model = tf.keras.models.load_model(transformer_model_path, custom_objects=custom_objects)
    
    # Prepare Transformer input data
    X_test_seq, Y_test_seq = prepare_transformer_data(test_params, test_zs, test_log_pks, ks)
    
    n_test = X_test_mlp.shape[0]
    
    # Benchmark inference time for MLP
    start_time = time.perf_counter()
    mlp_pred = mlp_model.predict(X_test_mlp, batch_size=32, verbose=0)
    end_time = time.perf_counter()
    mlp_inference_time = (end_time - start_time) / n_test
    
    # Benchmark inference time for Transformer
    start_time = time.perf_counter()
    transformer_pred = transformer_model.predict(X_test_seq, batch_size=32, verbose=0)
    end_time = time.perf_counter()
    transformer_inference_time = (end_time - start_time) / n_test
    
    # Compute performance metrics for MLP
    mlp_mse = np.mean((mlp_pred - test_log_pks)**2)
    mlp_max_rel_error = np.max(np.abs((mlp_pred - test_log_pks) / (np.abs(test_log_pks) + 1e-7)))
    
    # Process Transformer predictions: remove last dimension
    transformer_pred = np.squeeze(transformer_pred, axis=-1)  # shape: (n_test, num_k)
    transformer_mse = np.mean((transformer_pred - test_log_pks)**2)
    transformer_max_rel_error = np.max(np.abs((transformer_pred - test_log_pks) / (np.abs(test_log_pks) + 1e-7)))
    
    print("MLP Model Test MSE:", mlp_mse)
    print("MLP Model Maximum Relative Error:", mlp_max_rel_error)
    print("MLP Model Average Inference Time per Sample (s):", mlp_inference_time)
    
    print("Transformer Model Test MSE:", transformer_mse)
    print("Transformer Model Maximum Relative Error:", transformer_max_rel_error)
    print("Transformer Model Average Inference Time per Sample (s):", transformer_inference_time)
    
    # Plot predicted vs true power spectra for one test sample (here the first sample)
    sample_idx = 0
    true_log_pk = test_log_pks[sample_idx]   # shape: (num_k,)
    ks_values = ks                          # shape: (num_k,)
    mlp_pred_sample = mlp_pred[sample_idx]    # shape: (num_k,)
    transformer_pred_sample = transformer_pred[sample_idx]  # shape: (num_k,)
    
    # Convert from log space to original power spectra
    true_pk = np.exp(true_log_pk)
    mlp_pk = np.exp(mlp_pred_sample)
    transformer_pk = np.exp(transformer_pred_sample)
    
    # Create subplots for visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot for MLP model
    axes[0].set_title("MLP Model")
    axes[0].loglog(ks_values, true_pk, label="True", marker="o", linestyle="-")
    axes[0].loglog(ks_values, mlp_pk, label="Predicted", marker="x", linestyle="--")
    axes[0].set_xlabel(r"$k$")
    axes[0].set_ylabel(r"$P(k)$")
    axes[0].grid(True)
    axes[0].legend()
    axes[0].relim()
    axes[0].autoscale_view()
    
    # Plot for Transformer model
    axes[1].set_title("Transformer Model")
    axes[1].loglog(ks_values, true_pk, label="True", marker="o", linestyle="-")
    axes[1].loglog(ks_values, transformer_pk, label="Predicted", marker="x", linestyle="--")
    axes[1].set_xlabel(r"$k$")
    axes[1].set_ylabel(r"$P(k)$")
    axes[1].grid(True)
    axes[1].legend()
    axes[1].relim()
    axes[1].autoscale_view()
    
    plt.tight_layout()
    plot_path = os.path.join(data_dir, "predicted_vs_true.png")
    plt.savefig(plot_path, dpi=300)
    print("Predicted vs True power spectra plot saved to", plot_path)
    
    # Determine best architecture based on performance and inference speed
    if mlp_mse < transformer_mse and mlp_inference_time < transformer_inference_time:
        best_architecture = "MLP"
    elif transformer_mse < mlp_mse and transformer_inference_time < mlp_inference_time:
        best_architecture = "Transformer"
    else:
        best_architecture = "MLP" if mlp_mse < transformer_mse else "Transformer"
    
    print("Best architecture based on performance and speed:", best_architecture)

if __name__ == "__main__":
    main()