# Z shell kernel for Jupyter

![example screenshot](misc/example.png)

## Install

### Pipenv
[`install.sh`](misc/install.sh)
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
[`lab.sh`](misc/lab.sh)
```sh
pipenv run jupyter notebook
```
