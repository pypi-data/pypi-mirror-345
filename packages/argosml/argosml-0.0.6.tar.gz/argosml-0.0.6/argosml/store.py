import os, json

import numpy as np

class NumpyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.ndarray):
      # Replace inf and -inf with 0
      obj = np.where(np.isinf(obj), 0, obj)
      return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()  # Convert to native Python type
    return super().default(obj) 

def get_json_uri(data):
  data = json.dumps(data, cls=NumpyEncoder)
  output_path = 'temp_json/output.json'
  with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

  return output_path
