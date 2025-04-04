# master_graduation_project

TODO: Add reference somewhere to https://apimlqv2.tenwiseservice.nl/html/index.html

## How to use
- Create an venv and install the dependent libraries (see 'Requirements' in this read me).
- TODO:Make sure the following folder structure is present. 
- Change the file name of `config_template.yaml` to `config.yaml`, and change the variables accordingly.
- TODO: Make sure that `config.yaml` is in the same location as `main`.
- TODO: Run the application by entering `bash main.sh` in the terminal.

## Configuration
TODO: Please use `config.yaml` to modify the path of output folders, the verbosity of the logger can be changed and its filename.

## Folder structure
### Initial structure
### Example while running

## Workflow graph

## Data source

## Requirements
- Python:
Please [create your own Python (version 3.11.2) virtual environment](https://jennefer.gitbook.io/back-to-basic/initialize-project/create-a-new-python-venv) and install requirements by entering `pip install -r requirements.txt`. 
- Docker, following version was used: Docker version 20.10.24+dfsg1, build 297e128
- GROBID: lfoppiano/grobid:0.8.1 


-------


## Design choices
- The supervisor requested a modulair pipeline, where blocks in the pipeline would be easy to replaced.