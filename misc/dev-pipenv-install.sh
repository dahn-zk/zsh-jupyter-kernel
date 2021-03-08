rm -rf "../src/jupyter-kernel-test/pip-wheel-metadata"

pipenv --python 3
pipenv uninstall --all
pipenv install --dev
pipenv run python -m zsh_jupyter_kernel.install --sys-prefix

pipenv shell
