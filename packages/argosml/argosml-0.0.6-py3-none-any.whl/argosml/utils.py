from datetime import datetime

def generate_run_name(options, experiment_name):
    if options is None:
         return ''
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    
    run_naming_scheme = options.get("run_naming_scheme")
    custom_run_name = options.get("custom_run_name", "").strip()

    if run_naming_scheme == "timestamp":
        if custom_run_name:
            return f"{custom_run_name}_{timestamp}"
        return f"{experiment_name}_{timestamp}"
    
    if custom_run_name:
        return custom_run_name

    return ''