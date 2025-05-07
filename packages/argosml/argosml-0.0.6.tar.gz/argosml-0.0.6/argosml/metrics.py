# Import time module for performance debugging
import time

import numpy as np

from sklearn.metrics import roc_curve, auc, precision_recall_curve, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.calibration import calibration_curve

from sklearn.inspection import permutation_importance

import numpy as np
from sklearn.inspection import permutation_importance

def prepare_data_distributions(X_train, model=None, y_train=None, features_to_visualize=None, top_n=5):
    """
    Prepares histogram or frequency data for selected features to be visualized in Apache ECharts.

    If no features are provided, the function will attempt to select the top_n features based on importance:
      - First, it checks if the model has a 'coef_' attribute (e.g., LogisticRegression).
      - If not, it checks for 'feature_importances_' (e.g., RandomForest, XGBoost).
      - If neither is available, it uses permutation importance (requires y_train).

    Args:
        X_train (pd.DataFrame): The training dataset.
        model (optional): A trained model that may provide feature importance.
        y_train (array-like, optional): Target values; required if permutation importance is used.
        features_to_visualize (list[dict], optional): List of dicts specifying features to visualize.
            Each dict should have:
                - "name" (str): the feature/column name
                - "categorical" (bool, optional): True => treat as categorical, False => numeric
            If None or empty, the function determines the top_n features (all treated as numeric).
        top_n (int): Number of top features to select if features_to_visualize is empty.

    Returns:
        dict: A JSON-serializable dictionary with keys = feature names, values = distribution info.

        Example for numeric:
            {
              "bin_edges": [...],
              "counts": [...],
              "categorical": false
            }

        Example for categorical:
            {
              "bin_edges": ["A", "B", "C"],
              "counts": [10, 25, 5],
              "categorical": true
            }
    """

    # If no features are provided, do fallback logic to select top_n numeric features
    if not features_to_visualize:
        fallback_features = []
        if model is not None:
            # Case 1: Model provides coefficients (e.g., LogisticRegression)
            if hasattr(model, 'coef_'):
                importance = np.abs(model.coef_).flatten()
                top_idx = np.argsort(importance)[::-1][:top_n]
                fallback_features = [{"name": X_train.columns[i], "categorical": False} for i in top_idx]
            # Case 2: Model provides feature_importances_ (e.g., RandomForest, XGBoost)
            elif hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                top_idx = np.argsort(importance)[::-1][:top_n]
                fallback_features = [{"name": X_train.columns[i], "categorical": False} for i in top_idx]
            # Case 3: Permutation importance if y_train is provided
            elif y_train is not None:
                result = permutation_importance(model, X_train, y_train, n_repeats=10, random_state=42)
                importance = result.importances_mean
                top_idx = np.argsort(importance)[::-1][:top_n]
                fallback_features = [{"name": X_train.columns[i], "categorical": False} for i in top_idx]
            else:
                print("No feature importance info available and y_train not provided; returning empty distribution.")
        else:
            print("No model provided; returning empty distribution.")

        features_to_visualize = fallback_features

    # If still empty, return an empty dictionary
    if not features_to_visualize:
        return {}

    distribution_data = {}
    for feat_info in features_to_visualize:
        feature_name = feat_info["name"]
        is_categorical = feat_info.get("categorical", False)

        if feature_name not in X_train.columns:
            print(f"Warning: Feature '{feature_name}' not found in the dataset.")
            continue

        # Drop NaNs
        values = X_train[feature_name].dropna()

        # Convert booleans to int if it's not explicitly marked as categorical
        if values.dtype == bool and not is_categorical:
            values = values.astype(int)

        if is_categorical:
            # Categorical: treat unique values as 'bin_edges'
            vc = values.value_counts()
            bin_edges = vc.index.astype(str).tolist()
            counts = vc.values.tolist()
            distribution_data[feature_name] = {
                "bin_edges": bin_edges,
                "counts": counts,
                "categorical": True
            }
        else:
            # Numeric histogram
            hist, bin_edges = np.histogram(values, bins=20)
            distribution_data[feature_name] = {
                "bin_edges": bin_edges.tolist(),
                "counts": hist.tolist(),
                "categorical": False
            }

    return distribution_data

# def prepare_data_distributions(X_train, model=None, y_train=None, features_to_visualize=None, top_n=5):
#     """
#     Prepares histogram data for selected numerical features to be visualized in Apache ECharts.

#     If no features are provided, the function will attempt to select the top_n features based on importance:
#       - First, it checks if the model has a 'coef_' attribute.
#       - If not, it checks for a 'feature_importances_' attribute.
#       - If neither is available, it uses permutation importance (requires y_train).

#     Args:
#         X_train (pd.DataFrame): The training dataset.
#         model (optional): A trained model that may provide feature importance.
#         y_train (array-like, optional): Target values; required if permutation importance is used.
#         features_to_visualize (list, optional): List of feature names to visualize.
#             If None or empty, the function determines the top_n features based on importance.
#         top_n (int): Number of top features to select if features_to_visualize is not provided.

#     Returns:
#         dict: A JSON-serializable dictionary containing histogram data for the selected features,
#               or an empty dictionary if no features are available.
#     """
#     # If no features are provided, try to determine top features by importance
#     if not features_to_visualize:
#         features_to_visualize = []
#         if model is not None:
#             # Case 1: Model provides coefficients (e.g. LogisticRegression)
#             if hasattr(model, 'coef_'):
#                 importance = np.abs(model.coef_).flatten()
#                 top_idx = np.argsort(importance)[::-1][:top_n]
#                 features_to_visualize = [X_train.columns[i] for i in top_idx]
#             # Case 2: Model provides feature_importances_ (e.g. RandomForest, XGBoost)
#             elif hasattr(model, 'feature_importances_'):
#                 importance = model.feature_importances_
#                 top_idx = np.argsort(importance)[::-1][:top_n]
#                 features_to_visualize = [X_train.columns[i] for i in top_idx]
#             # Case 3: Fall back on permutation importance if y_train is provided
#             elif y_train is not None:
#                 result = permutation_importance(model, X_train, y_train, n_repeats=10, random_state=42)
#                 importance = result.importances_mean
#                 top_idx = np.argsort(importance)[::-1][:top_n]
#                 features_to_visualize = [X_train.columns[i] for i in top_idx]
#             else:
#                 print("No feature importance information available and y_train not provided; returning empty distribution.")
#         else:
#             print("No model provided; returning empty distribution.")

#     # If still empty, return an empty dictionary
#     if not features_to_visualize:
#         return {}

#     distribution_data = {}
#     for column in features_to_visualize:
#         if column in X_train.columns:
#             values = X_train[column].dropna()
#             # Cast booleans to int to avoid warning
#             if values.dtype == bool:
#                 values = values.astype(int)
#             hist, bin_edges = np.histogram(values, bins=20)
#             distribution_data[column] = {
#                 "bin_edges": bin_edges.tolist(),
#                 "counts": hist.tolist()
#             }
#         else:
#             print(f"Warning: Feature '{column}' not found in the dataset.")

#     return distribution_data

def prepare_roc(y_test, y_pred_proba):
    # Calculate ROC curve points
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

    # Calculate AUC
    roc_auc = auc(fpr, tpr)

    return {
        'fpr': fpr,
        'tpr': tpr,
        'thresh': thresholds,
        'roc_auc': roc_auc
    }

def prepare_pr(y_test, y_pred_proba):
    precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
    auc_prc = auc(recall, precision)
    prc_dict = {
        'precision': precision,
        'recall': recall,
        'thresh': thresholds,
        'auc_prc': auc_prc
    }        
    return prc_dict

# Note: Binning approach used by sklearn for calculating probability calibration may result in problems such as information loss or discontinuities, 
# alternative smooth calibration methods such as Loess (Locally Estimated Scatterplot Smoothing) exist and are implemented in other libraries. 
# Still, the binning approach is a good baseline approach and widely used/understood. 

# TODO: try sklearn's IsotonicRegression module instead for calculating the calibration curve.

# iso_reg = IsotonicRegression(out_of_bounds="clip")
# prob_pred_iso = iso_reg.fit_transform(y_pred_proba, y_test)
# plt.plot(prob_pred, prob_true, label="Binned Calibration")
# plt.plot(prob_pred_iso, prob_true, label="Isotonic Calibration")
# plt.legend()
# plt.show()

# TODO: Add cross-validation to test robustness of calibration curve. Plot cross validated curves as alongside.
def prepare_probability_calibration(y_test, y_pred_proba, n_bins=10):
    """
    Calculate calibration curve points.
    
    Parameters:
        y_test (array-like): True labels.
        y_pred_proba (array-like): Predicted probabilities.
        n_bins (int): Number of bins to use for the calibration curve.
    
    Returns:
        dict: Dictionary containing the calibration curve values.
    """
    # Temp binning rules: 10 bins minimum, or 20 if > 5k samples, 50 if > 10k 
    if len(y_pred_proba) > 10000:
        n_bins = 50
    elif len(y_pred_proba) > 5000:
        n_bins = 20

    # Calculate calibration curve points
    prob_true, prob_pred = calibration_curve(y_test, y_pred_proba, n_bins=n_bins, strategy='uniform')
    
    return {
        'prob_true': prob_true,  # y-axis values for calibration curve
        'prob_pred': prob_pred,  # x-axis values for calibration curve
    }

def prepare_probability_counts(y_test, y_pred_proba, n_bins=10):
    # Temp binning rules: 10 bins minimum, or 20 if > 5k samples, 50 if > 10k 
    if len(y_pred_proba) > 10000:
        n_bins = 50
    elif len(y_pred_proba) > 5000:
        n_bins = 20

    bins = np.linspace(0, 1, n_bins + 1)  # Bins from 0.0 to 1.0
    bin_labels = [f"{bins[i]:.2f} - {bins[i+1]:.2f}" for i in range(n_bins)]

    # Assign predicted probabilities to bins and calculate counts
    bin_indices = np.digitize(y_pred_proba, bins, right=True) - 1  # Adjust indices to 0-based
    bin_counts = [sum(bin_indices == i) for i in range(n_bins)]

    fraction_positives = [
        np.mean(y_test[bin_indices == i]) if bin_counts[i] > 0 else None  # Avoid division by zero
        for i in range(n_bins)
    ]

    results = { 
        'probability_range': bin_labels, 
        'count': bin_counts,
        'fraction_positives': fraction_positives
    }

    print(results)

    return results

def calculate_accuracy(y_true, y_pred):
    """
    Calculate accuracy score.
    
    Parameters:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.
    
    Returns:
        float: The accuracy score.
    """
    return accuracy_score(y_true, y_pred)

