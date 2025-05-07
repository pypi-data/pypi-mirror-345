# Argos Tracker Getting Started
- Clone Repo
- Make sure Anaconda is installed
- Create conda env with ```conda env create --name argos-tracker --file=environment.yml```
- To update previously created envs use ```conda env update --file environment.yml --prune```

## Jupyter Lab
- Activate conda env with ```conda activate argos-tracker```
- Create project specific ipykernel if it has not been created yet:
```
python -m ipykernel install --user --name argos-tracker --display-name "argos-tracker"
```
- Start jupyter lab: ```jupyter lab```
- Open client using link provided on start
- Open test_notebook_mimic.ipynb and select the argos-tracker ipykernel

## MLflow
- Open a new terminal window and activate the argos-tracker env
- Start mlflow: ```mlflow server --host 127.0.0.1 --port 8787 --app-name mlflow_cors```

## Argos Dashboard
- In a third terminal window activate the argos-tracker env
- Go to the reports_dashboard directory ```cd reports_dashboard```
- Run ```npm ci``` to install dependencies for Vue frontend
- The following error may occur if using ubuntu with a version older than 24.04: 
```
node: /lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.31' not found (required by /home/user/anaconda3/envs/argos-tracker/bin/../lib/libnode.so.127)
```
- Start client with ```npm run dev```
