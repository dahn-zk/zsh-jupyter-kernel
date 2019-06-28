pipenv --python 3.7 jupyter-notebook
pipenv install --editable .
pipenv run python -m zsh_kernel.install --sys-prefix
