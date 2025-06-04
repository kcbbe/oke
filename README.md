**Open Knowledge Explorer**

Please find the github page containing [the code over here](https://github.com/CharmingChocobo/master_graduation_project/tree/main) and
check out [this extensive documentation page](https://bioinf.nl/~jbeenen/oke/html/index.html).

TODO: Add reference somewhere to https://apimlqv2.tenwiseservice.nl/html/index.html

## How to use
- Create an venv and install the dependent libraries (see 'Requirements' on this page).
- TODO:Make sure the following folder structure is present. 
- Change the file name of `config_template.yaml` to `config.yaml`, and change the variables accordingly.
- TODO: Make sure that `config.yaml` is in the same location as `main`.
- TODO: Run the application by entering `bash main.sh` in the terminal.

## Configuration
TODO: Please use `config.yaml` to modify the path of output folders, the verbosity of the logger can be changed and its filename.

## Folder structure
**TODO: Initial structure**

```bash
.
├── df_all_int/
├── df_training/
├── logs/
├── model/
│   └── model_name.model
└── report/
    └── report_dmt.txt
```
**TODO: Example while running**
```bash
.
├── df_all_int/
├── df_training/
├── logs/
├── model/
│   └── model_name.model
└── report/
    └── report_dmt.txt
```
## Workflow graph
TODO: place flowchart
## Data source
_TenWise KMAP:_
https://apimlqv2.tenwiseservice.nl/html/index.html

_OpenAlex:_
Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833

## Requirements
- Python: version 3.11.2, see `requirements.txt` for required libraries.
_(Please check out [this gitbook](https://jennefer.gitbook.io/back-to-basic/initialize-project/create-a-new-python-venv) on how to create a virtual environment and quick install required libraries.)_
- TODO: replace: Docker, following version was used: Docker version 20.10.24+dfsg1, build 297e128
- TODO: GROBID: lfoppiano/grobid:0.8.1 

## Design choices
The supervisor requested a modulair pipeline, where blocks in the pipeline would be easy to replaced.