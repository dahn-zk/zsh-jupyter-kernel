# Z shell kernel for Jupyter

![example screenshot](./example.png)

## Install

### Pipenv
[`install.sh`](./install.sh)
```sh
pipenv --python 3.7 install zsh-kernel jupyter-notebook
pipenv run python -m zsh_kernel.install --sys-prefix
```

### Pip
```sh
python -m pip install zsh-kernel
python -m zsh_kernel.install
```

## Run
[`lab.sh`](./lab.sh)
```sh
pipenv run jupyter notebook
```
