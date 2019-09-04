rm -rf src/jupyter-kernel-test/pip-wheel-metadata

PIPENV_VERBOSITY=-1 pipenv --python 3.7
PIPENV_VERBOSITY=-1 pipenv uninstall --all
PIPENV_VERBOSITY=-1 pipenv install --dev
PIPENV_VERBOSITY=-1 pipenv run python -m zsh_jupyter_kernel.install --sys-prefix

PIPENV_VERBOSITY=-1 pipenv shell
