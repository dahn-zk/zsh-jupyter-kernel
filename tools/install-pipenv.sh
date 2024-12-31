# deactivate conda environments if any
conda deactivate

# remove any pipenvs
pipenv --rm

# check pipenv
pipenv --version; which pipenv

# create environment
pipenv --python 3.8

# install dependencies and kernel
pipenv update
pipenv run python -m zsh_jupyter_kernel.install --name zsh --display-name "Z shell (dev)" --sys-prefix

# quick test
pipenv run jupyter console --kernel=zsh

# notes:
# - `pipenv uninstall --all` removes some packages which are necessary for further functioning, so don't clean environment such way
