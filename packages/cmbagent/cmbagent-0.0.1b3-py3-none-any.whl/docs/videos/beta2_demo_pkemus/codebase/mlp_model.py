# filename: codebase/mlp_model.py
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.callbacks import EarlyStopping

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

def build_mlp_model(input_dim, output_dim):
    r"""
    Build a Multilayer Perceptron (MLP) model.
    
    Args:
        input_dim (int): Dimension of the input features.
        output_dim (int): Dimension of the output vector (number of k bins).
        
    Returns:
        tf.keras.Model: Compiled Keras model.
    """
    model = Sequential([
        Input(shape=(input_dim,)),
        Dense(128, activation='relu'),
        Dense(128, activation='relu'),
        Dense(128, activation='relu'),
        Dense(output_dim, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def main():
    r"""
    Main function to train and evaluate the first neural network (MLP) for predicting
    the linear matter power spectrum.
    
    The function performs the following steps:
        1. Loads the training and testing datasets from the 'data/' directory.
        2. Prepares input features by concatenating cosmological parameters and redshift.
        3. Builds and compiles an MLP model.
        4. Trains the model using the training dataset and validates on the testing dataset.
        5. Evaluates model performance using mean squared error (MSE) and maximum relative error.
        6. Saves the trained model and training history in the 'data/' directory.
    """
    # Set seeds for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    data_dir = "data"
    train_file = os.path.join(data_dir, "training_dataset.npz")
    test_file = os.path.join(data_dir, "testing_dataset.npz")
    
    # Load training and testing datasets
    train_params, train_zs, train_log_pks, ks = load_dataset(train_file)
    test_params, test_zs, test_log_pks, _ = load_dataset(test_file)
    
    # Prepare input: concatenate cosmological parameters and redshift (reshape zs to (num_samples, 1))
    train_zs = train_zs.reshape(-1, 1)
    test_zs = test_zs.reshape(-1, 1)
    X_train = np.concatenate([train_params, train_zs], axis=1)  # Shape: (num_train, 7)
    X_test = np.concatenate([test_params, test_zs], axis=1)      # Shape: (num_test, 7)
    
    Y_train = train_log_pks  # Shape: (num_train, num_k)
    Y_test = test_log_pks    # Shape: (num_test, num_k)
    
    input_dim = X_train.shape[1]   # Should be 7
    output_dim = Y_train.shape[1]  # Number of k bins
    
    # Build the MLP model
    model = build_mlp_model(input_dim, output_dim)
    
    # Set up early stopping to avoid overfitting
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # Train the model
    history = model.fit(X_train, Y_train, 
                        validation_data=(X_test, Y_test), 
                        epochs=100, 
                        batch_size=32, 
                        callbacks=[early_stop],
                        verbose=1)
    
    # Evaluate the model on test data
    test_loss = model.evaluate(X_test, Y_test, verbose=0)
    print("Test MSE (loss):", test_loss)
    
    # Compute maximum relative error over the test dataset
    Y_pred = model.predict(X_test)
    # Element-wise relative error; adding small constant to avoid division by zero
    relative_errors = np.abs((Y_pred - Y_test) / (np.abs(Y_test) + 1e-7))
    max_relative_error = np.max(relative_errors)
    print("Maximum relative error:", max_relative_error)
    
    # Save the trained model and training history
    model_path = os.path.join(data_dir, "mlp_model.h5")
    model.save(model_path)
    print("Trained MLP model saved to", model_path)
    
    history_path = os.path.join(data_dir, "mlp_training_history.npy")
    np.save(history_path, history.history)
    print("Training history saved to", history_path)

if __name__ == "__main__":
    main()
