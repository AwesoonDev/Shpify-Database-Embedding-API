Project Name
========

Small project description


Development
-----------
### Dependencies

Our chosen dependency manager for ML projects is [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html).

First, make sure you have the necessary environment variables set. To create or update the project's depencencies, run:
```sh
make setup
```

To update the conda environment `mymlenv` with the dependencies file `environment.yml`:
```sh
conda activate mymlenv
```

### Unit tests and linting
```sh
tox
```

How to use it
=============

Launch these commands to run the flask service:

```sh
make run
```
