
import numpy as np

def categorical_crossentropy(y_true_batch, y_pred_batch):
    epsilon = 1e-7
    y_pred_batch = np.clip(y_pred_batch, epsilon, 1. - epsilon)
    
    losses = -np.sum(y_true_batch * np.log(y_pred_batch), axis=1)

    mean_loss = np.mean(losses)
    return mean_loss


def binary_crossentropy(y_true_batch, y_pred_batch):
    epsilon = 1e-7
    y_pred_batch = np.clip(y_pred_batch, epsilon, 1. - epsilon)
    
    losses = -np.mean(y_true_batch * np.log(y_pred_batch) + (1 - y_true_batch) * np.log(1 - y_pred_batch), axis=1)

    mean_loss = np.mean(losses)
    return mean_loss

def categorical_crossentropy_derivative(y_true, y_pred):
    epsilon = 1e-7
    y_pred = np.clip(y_pred, epsilon, 1. - epsilon)
    return - (y_true / y_pred)

def binary_crossentropy_derivative(y_true, y_pred):
    epsilon = 1e-7
    y_pred = np.clip(y_pred, epsilon, 1. - epsilon)
    return (y_pred - y_true) / (y_pred * (1 - y_pred))
