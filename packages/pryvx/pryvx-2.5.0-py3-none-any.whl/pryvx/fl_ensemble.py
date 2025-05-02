import numpy as np

def federated_ensemble(estimators, X_test):
    """
    Perform soft voting ensemble on a list of trained estimators.
    
    :param estimators: List of trained models that support `predict_proba`
    :param X_test: Test dataset (features only)
    :return: Final predictions after soft voting
    """
    if not estimators:
        raise ValueError("No models provided for ensemble.")

    # Sum all probability predictions
    avg_probs = sum(model.predict_proba(X_test) for model in estimators) / len(estimators)

    # Convert probabilities to final predictions (highest probability wins)
    y_pred_ensemble = np.argmax(avg_probs, axis=1)
    
    return y_pred_ensemble