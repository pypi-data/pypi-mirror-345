# filename: codebase/transformer_model.py
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention
from tensorflow.keras.models import Model
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

def prepare_transformer_data(params, zs, log_pks, ks):
    r"""
    Prepare input features and targets for the transformer model.
    
    For each sample, we form a sequence of tokens of length equal to the number
    of k values. Each token is constructed by concatenating the scalar k value and the 
    constant cosmological features (parameters and redshift) for that sample.
    
    Args:
        params (np.ndarray): Array of cosmological parameters (shape: [num_samples, 6]).
        zs (np.ndarray): Array of redshift values (shape: [num_samples,]).
        log_pks (np.ndarray): Array of log-transformed power spectra (shape: [num_samples, num_k]).
        ks (np.ndarray): Array of wavenumber values (shape: [num_k,]).
    
    Returns:
        tuple: A tuple (X_seq, Y_seq) where:
            - X_seq (np.ndarray): Input sequence for the transformer with shape (num_samples, num_k, 8),
                                  each token is [k, param1, ..., param6, z].
            - Y_seq (np.ndarray): Target sequence with shape (num_samples, num_k, 1).
    """
    n_samples = params.shape[0]
    num_k = ks.shape[0]
    # Concatenate cosmological parameters and redshift to form a (num_samples, 7) array.
    X_base = np.concatenate([params, zs.reshape(-1, 1)], axis=1)
    # Repeat the constant features along the sequence length (num_k).
    X_base_rep = np.repeat(X_base[:, np.newaxis, :], num_k, axis=1)  # shape: (n_samples, num_k, 7)
    # Expand the k vector to shape (1, num_k, 1) and tile for each sample.
    ks_rep = np.tile(ks.reshape(1, num_k, 1), (n_samples, 1, 1))
    # Concatenate the k values with the repeated cosmological features.
    X_seq = np.concatenate([ks_rep, X_base_rep], axis=2)  # shape: (n_samples, num_k, 8)
    # Reshape targets to have an extra dimension.
    Y_seq = log_pks[..., np.newaxis]  # shape: (n_samples, num_k, 1)
    return X_seq, Y_seq

def transformer_block(x, embed_dim, num_heads, ff_dim, dropout=0.1):
    r"""
    Defines a single transformer block.
    
    Args:
        x (tf.Tensor): Input tensor.
        embed_dim (int): Dimension of the embedding.
        num_heads (int): Number of attention heads.
        ff_dim (int): Dimension of the feed-forward network.
        dropout (float): Dropout rate.
    
    Returns:
        tf.Tensor: Output tensor after applying the transformer block.
    """
    attn_output = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)(x, x)
    attn_output = Dropout(dropout)(attn_output)
    out1 = LayerNormalization(epsilon=1e-6)(x + attn_output)
    ffn_output = Dense(ff_dim, activation="relu")(out1)
    ffn_output = Dense(embed_dim)(ffn_output)
    ffn_output = Dropout(dropout)(ffn_output)
    return LayerNormalization(epsilon=1e-6)(out1 + ffn_output)

def build_transformer_model(seq_len, input_dim, embed_dim=32, num_heads=4, ff_dim=64, num_transformer_blocks=2):
    r"""
    Build a transformer model for sequence-to-sequence regression.
    
    The model projects the input tokens into a learnable embedding space, passes them through
    a stack of transformer blocks, and then applies a token-wise Dense layer to produce predictions.
    
    Args:
        seq_len (int): Length of the input sequence (number of k bins).
        input_dim (int): Dimension of each token in the input sequence.
        embed_dim (int): Dimension of the embedding space.
        num_heads (int): Number of attention heads in the MultiHeadAttention layer.
        ff_dim (int): Dimension of the feed-forward network within the transformer block.
        num_transformer_blocks (int): Number of transformer blocks to stack.
    
    Returns:
        tf.keras.Model: Compiled transformer model.
    """
    inputs = Input(shape=(seq_len, input_dim))
    # Project input tokens to the embedding dimension.
    x = Dense(embed_dim)(inputs)
    # Apply a stack of transformer blocks.
    for _ in range(num_transformer_blocks):
        x = transformer_block(x, embed_dim, num_heads, ff_dim)
    # Token-wise regression head: project each token to a single output.
    outputs = Dense(1, activation='linear')(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mse')
    return model

def main():
    r"""
    Main function to train and evaluate a transformer-based neural network for predicting
    the log-transformed linear matter power spectrum.
    
    Steps performed:
      1. Load the training and testing datasets from the 'data/' directory.
      2. Prepare input sequences by combining the shared k-grid with the repeated cosmological parameters and redshift.
      3. Build and compile the transformer model.
      4. Train the model using early stopping based on validation loss.
      5. Evaluate the model performance using MSE and maximum relative error.
      6. Save the trained model and training history in the 'data/' directory.
    """
    # Set seeds for reproducibility.
    np.random.seed(42)
    tf.random.set_seed(42)
    
    data_dir = "data"
    train_file = os.path.join(data_dir, "training_dataset.npz")
    test_file = os.path.join(data_dir, "testing_dataset.npz")
    
    # Load training and testing datasets.
    train_params, train_zs, train_log_pks, ks = load_dataset(train_file)
    test_params, test_zs, test_log_pks, _ = load_dataset(test_file)
    
    # Prepare data for the transformer: generate input sequences and reshape targets.
    X_train_seq, Y_train_seq = prepare_transformer_data(train_params, train_zs, train_log_pks, ks)
    X_test_seq, Y_test_seq = prepare_transformer_data(test_params, test_zs, test_log_pks, ks)
    
    seq_len = X_train_seq.shape[1]  # Number of k bins.
    input_dim = X_train_seq.shape[2]  # Should be 8.
    
    # Build the transformer model.
    model = build_transformer_model(seq_len, input_dim, embed_dim=32, num_heads=4, ff_dim=64, num_transformer_blocks=2)
    model.summary()
    
    # Set up early stopping.
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    # Train the model.
    history = model.fit(X_train_seq, Y_train_seq, 
                        validation_data=(X_test_seq, Y_test_seq),
                        epochs=100, 
                        batch_size=32,
                        callbacks=[early_stop],
                        verbose=1)
    
    # Evaluate the model.
    test_loss = model.evaluate(X_test_seq, Y_test_seq, verbose=0)
    print("Test MSE (loss):", test_loss)
    
    # Compute maximum relative error.
    Y_pred_seq = model.predict(X_test_seq)
    relative_errors = np.abs((Y_pred_seq - Y_test_seq) / (np.abs(Y_test_seq) + 1e-7))
    max_relative_error = np.max(relative_errors)
    print("Maximum relative error:", max_relative_error)
    
    # Save the trained model and training history.
    model_path = os.path.join(data_dir, "transformer_model.keras")
    model.save(model_path)
    print("Trained Transformer model saved to", model_path)
    
    history_path = os.path.join(data_dir, "transformer_training_history.npy")
    np.save(history_path, history.history)
    print("Training history saved to", history_path)

if __name__ == "__main__":
    main()