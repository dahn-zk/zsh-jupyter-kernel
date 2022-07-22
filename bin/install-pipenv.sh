# deactivate conda environments if any
conda deactivate

# remove any pipenvs
pipenv --rm

# check pipenv
pipenv --version; which pipenv

# forgot wtf is this
rm -rf "../src/jupyter-kernel-test/pip-wheel-metadata"

# create environment
pipenv --python 3.8

# install dependencies and kernel
pipenv install --dev
pipenv run python -m zsh_jupyter_kernel.install --sys-prefix

# quick test
pipenv run jupyter console --kernel=zsh

# notes:
# - `pipenv uninstall --all` removes some packages which are necessary for further functioning, so don't clean environment such way
