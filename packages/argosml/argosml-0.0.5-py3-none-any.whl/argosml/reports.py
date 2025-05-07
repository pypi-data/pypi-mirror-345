from jinja2 import Environment, FileSystemLoader
import os

def check_write_permissions(path):
    # Check if the directory exists
    if not os.path.exists(path):
        print(f"The directory {path} does not exist.")
        return False
    
    # Check if it's a directory
    if not os.path.isdir(path):
        print(f"{path} is not a directory.")
        return False
    
    # Check for write permissions
    if os.access(path, os.W_OK):
        print(f"You have write permissions in {path}")
        return True
    else:
        print(f"You do NOT have write permissions in {path}")
        return False
    
def init_report(experiment_id, run_id, argos_uri, custom_metrics=None):
  return _render_html(experiment_id, run_id, argos_uri)
   
# Renders html used to redirect to Argos Reports Dashboard
def _render_html(experiment_id, run_id, argos_uri) -> str:  
  # Specify the directory where your template is located
  template_dir = os.path.join(os.path.dirname(__file__), 'jinja/templates')

  # Set up the Jinja2 environment
  env = Environment(loader=FileSystemLoader(template_dir), auto_reload=True)

  # May need to clear cache after changing template
  env.cache.clear()

  # Load the template
  template = env.get_template('redirect.html')

  data = {
    'experiment_id': experiment_id,
    'run_id': run_id,
    'argos_uri': argos_uri
  }

  # Generate html
  output = template.render(data)  

  output_path = 'temp_html/argos_reports_dashboard.html'
  # Write generated html to a file
  with open(output_path, 'w') as f:
    f.write(output)

  return output_path