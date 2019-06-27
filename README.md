# Z shell kernel for Jupyter

![example screenshot](./example.png)

## Install
[`install.sh`](./install.sh)
```sh
pipenv --python 3.7
pipenv install jupyter
pipenv install --editable .
pipenv run python -m zsh_kernel.install --sys-prefix
```

## Run
[`lab.sh`](./lab.sh)
```sh
pipenv run jupyter notebook
```
