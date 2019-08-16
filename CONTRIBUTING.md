# Contributing

## Install editable package
[`dev-install.sh`](./dev-install.sh)
```sh
pipenv --python 3.7
pipenv install --dev
pipenv run python -m zsh_jupyter_kernel.install --sys-prefix
```
By executing above commands you install development packages in editable
mode, which means that the packages will be served directly from sources, 
so you'll be able to immediately test your change without re-installing. 

## [Keep a changelog](https://keepachangelog.com/en/0.3.0/)
