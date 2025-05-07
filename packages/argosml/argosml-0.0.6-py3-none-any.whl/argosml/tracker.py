# Import time module for performance debugging
import time
import os
import json
import mlflow
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from pathlib import Path
import webbrowser
import subprocess
import requests
from urllib.parse import urlparse
import logging

from argosml.fairness import fairness_metrics
from argosml.reports import init_report
from argosml.store import get_json_uri
from argosml.subcohort import subcohort_analysis
from argosml.metrics import *
from argosml.utils import *

# Global state
_server_uri = None
_experiment_name = None
_argos_uri = None

def init(server_uri: str = "http://127.0.0.1:8787", experiment_name: str = "Default", argos_uri: str = "http://127.0.0.1:8444"):
    """Initialize the tracker with server URI and experiment name."""
    global _server_uri, _experiment_name, _argos_uri
    _server_uri = server_uri
    _experiment_name = experiment_name
    _argos_uri = argos_uri
    mlflow.set_tracking_uri(_server_uri)
    mlflow.set_experiment(_experiment_name)

    # Enable autologging for sklearn only
    mlflow.sklearn.autolog()

def log_run(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, 
            model: BaseEstimator, fairness_params: Optional[Dict[str, Any]] = None, 
            options: Optional[Dict[str, Any]] = None) -> None:
    """Log a model run with metrics and visualizations."""
    if _server_uri is None or _experiment_name is None:
        raise ValueError("Tracker not initialized. Call init() first.")
    
    with mlflow.start_run():
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log parameters
        mlflow.log_params(model.get_params())
        
        # Log metrics
        metrics = calculate_metrics(X_train, y_train, X_test, y_test, model)
        mlflow.log_metrics(metrics)
        
        # Log fairness metrics if requested
        if fairness_params:
            fairness_metrics_dict = fairness_metrics(X_test, y_test, model, fairness_params)
            mlflow.log_metrics(fairness_metrics_dict)
        
        # Log visualizations
        log_visualizations(X_train, y_train, X_test, y_test, model, options)
        
        # Log feature importance
        log_feature_importance(X_train, y_train, model)
        
        # Log subcohort analysis if requested
        if options and options.get('subcohort_analysis'):
            subcohort_analysis(X_test, y_test, model, options['subcohort_analysis'])
        
        # Initialize report
        init_report(_argos_uri)

# def test_render(fairness_metrics):
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


