import numpy as np

from ..cpu.loss_functions import categorical_crossentropy, categorical_crossentropy_derivative
from ..cpu.activation_functions import apply_activation, apply_activation_derivative

def backprop_update_general(
    X, y, weights, activations_list,
    learning_rate=0.01
):
    """
    X: (batch_size, input_dim)
    y: (batch_size, output_dim)
    weights: numpy object array, her eleman (in_dim, out_dim) şeklinde ağırlık matrisi
    activations_list: her katman için aktivasyon ismi listesi (örn: ['relu', 'sigmoid', 'softmax'])
    apply_activation: x ve aktivasyon adı alır, çıktı verir
    apply_activation_derivative: x ve aktivasyon adı alır, türev verir
    loss_function: y_true ve y_pred alır, loss döner
    loss_derivative: y_true ve y_pred alır, d_loss/d_y_pred döner
    learning_rate: öğrenme oranı
    """
    num_layers = len(weights) + 1
    activations = [X]
    inputs = []
    
    # Forward pass
    for i, w in enumerate(weights):
        inp = np.dot(activations[-1], w)
        out = apply_activation(inp, activations_list[i])
        inputs.append(inp)
        activations.append(out)
    
    y_pred = activations[-1]
    loss = categorical_crossentropy(y, y_pred)
    
    # Calculate output error (using provided derivative)
    error = categorical_crossentropy_derivative(y, y_pred)
    deltas = [error * apply_activation_derivative(inputs[-1], activations_list[-1])]
    
    # Backpropagate
    for i in reversed(range(len(weights) - 1)):
        delta = np.dot(deltas[0], weights[i + 1].T) * apply_activation_derivative(inputs[i], activations_list[i])
        deltas.insert(0, delta)
    
    # Update weights
    for i in range(len(weights)):
        weights[i] += learning_rate * np.dot(activations[i].T, deltas[i])
    
    return weights, loss