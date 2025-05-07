import numpy as np
import pandas as pd
     
def calc_group_metrics(X_train, y_train, X_test, y_test, target):    
    pass

def subcohort_analysis(X_train, y_train, X_test, y_test, target_cols):    
    subcohort_metrics = []
    for target_col in target_cols:
        # Find the unique values in target_col
        subcohorts = y_train[target_col].unique().tolist()
        for subcohort in subcohorts:
            subcohort_metrics.append(calc_group_metrics(X_train, y_train, X_test, y_test, subcohort))

    return {
        'subcohort_metrics': subcohort_metrics
    }