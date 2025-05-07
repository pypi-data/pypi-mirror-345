# Import time module for performance debugging
import time

import numpy as np

import mlflow
from mlflow import MlflowClient

from sklearn.metrics import roc_curve, auc, precision_recall_curve
from sklearn.calibration import calibration_curve

from argosml.fairness import fairness_metrics
from argosml.reports import init_report
from argosml.store import get_json_uri
from argosml.subcohort import subcohort_analysis
from argosml.metrics import *
from argosml.utils import *

class SingletonState:
    _instance = None  # Class-level variable to hold the single instance

    def __new__(cls):
        if cls._instance is None:
            # Create a new instance and store it in _instance
            cls._instance = super(SingletonState, cls).__new__(cls)
            cls._instance.state = {}  # Initialize the state
        return cls._instance

    def set(self, key, value):
        self.state[key] = value

    def get(self, key):
        return self.state.get(key)
    
config = SingletonState()

def init(server_uri='http://localhost:8787', experiment_name="Untitled", argos_uri='http://localhost:8444'):
    # If port for argos is changed, the devServer port must also be updated in /reports_dashboard/quasar.config.js
    config.set('argos_uri', argos_uri)
    config.set('experiment_name', experiment_name)
    mlflow.set_tracking_uri(uri=server_uri)
    mlflow.set_experiment(experiment_name)

    # Enable autologging for sklearn only
    mlflow.sklearn.autolog()

def train_and_log_run(X_train, y_train, estimator):
    pass

# def test_render(fairness_metrics):
#     return generate_report(fairness_metrics)
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

def log_run(X_train, y_train, X_test, y_test, model, options=None, fairness_params=None, custom_metrics=None, subcohort_params=None, framework='sklearn', target_run=None):
    # Check that argos was initialized
    if config.get('argos_uri') is None:
        print("Make sure Argos was initialized correctly before logging.")
        return

    last_run = mlflow.last_active_run()

    if last_run:
        experiment_id = last_run.info.experiment_id
        run_id = last_run.info.run_id
        print(f"Experiment ID: {experiment_id}")
        print(f"Run ID: {run_id}")
    else:
        print("No run was found. Make sure training code triggered autologging.")
        return

    if framework == 'sklearn':
        # Make predictions
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        roc_dict = prepare_roc(y_test, y_pred_proba)      
        prc_dict = prepare_pr(y_test, y_pred_proba)   
        calibration_dict = prepare_probability_calibration(y_test, y_pred_proba)   
        probability_counts_dict = prepare_probability_counts(y_test, y_pred_proba)   
        data_store = {
            'prc': prc_dict,
            'roc': roc_dict,
            'calibration': calibration_dict,
            'probability_counts': probability_counts_dict
        }

        # Calculate standard metrics
        y_pred = model.predict(X_test)
        acc = calculate_accuracy(y_test, y_pred)

        # Subcohort analysis
        # Groups priority: 
        # If subcohort_params are given, perform subcohort analysis on the specified groups. 
        # If subcohort_params is not given but fairness_params are, perform analysis on protected variables specified in fairness_params.
        # If neither are provided, do nothing
        if subcohort_params is not None:
            pass
        elif fairness_params is not None:       
            pass     
            # print(fairness_params['protected_variables'])
            # subcohort_results = subcohort_analysis(X_train, y_train, X_test, y_test, fairness_params['protected_variables'])
            # data_store['subcohort'] = subcohort_results
        
        run_name = generate_run_name(options, config.get('experiment_name'))
       
        # Add our custom metrics to last run
        with mlflow.start_run(run_id=run_id, run_name=run_name) as run:  
            experiment_id = run.info.experiment_id    
            mlflow.set_tag("mlflow.runName", run_name)

            # Retrieve features to visualize from options (if provided)
            plot_features = options.get('plot_features') if options else None
            data_distributions_dict = prepare_data_distributions(X_train, model, y_train, features_to_visualize=plot_features, top_n=5)
            data_store['data_distributions'] = data_distributions_dict

            # Log standard metrics
            mlflow.log_metric('test_accuracy', acc)

            # Log fairness metrics
            if fairness_params is not None:
                # start = time.time()
                fairness_dict = fairness_metrics(X_train, y_train, model, **fairness_params)
                # end = time.time()
                # print the difference between start 
                # and end time in milli. secs
                # print("Execution time was:", (end-start) * 10**3, "ms")
                # Log fairness metrics
                for metric_name, value in fairness_dict.items():
                    mlflow.log_metric(metric_name, value)

            # Generate html and log as artifact
            html_path = init_report(experiment_id, run_id, config.get('argos_uri'))
            # 'temp_html/output.html'
            # html_path = 'argos_reports_dashboard.html'

            if html_path:
                mlflow.log_artifact(html_path)
                print('logged html artifact from path:')
                print(html_path)
            else:
                print('html path not found')

            # Save custom metrics to a json file and log as artifact 
            json_path = get_json_uri(data_store)
            if json_path:
                mlflow.log_artifact(json_path)
                print('logged json artifact from path:')
                print(json_path)
            else:
                print('json path not found')

class ArgosTracker:
    def __init__(self, server_uri='http://localhost:8787', experiment_name="Untitled", argos_uri='http://localhost:8444'):
        self.server_uri = server_uri
        self.experiment_name = experiment_name
        self.argos_uri = argos_uri
        init(server_uri, experiment_name, argos_uri)

    def log_run(self, X_train, y_train, X_test, y_test, model, options=None, fairness_params=None, custom_metrics=None, subcohort_params=None, framework='sklearn', target_run=None):
        return log_run(X_train, y_train, X_test, y_test, model, options, fairness_params, custom_metrics, subcohort_params, framework, target_run)

    def train_and_log_run(self, X_train, y_train, estimator):
        return train_and_log_run(X_train, y_train, estimator)


