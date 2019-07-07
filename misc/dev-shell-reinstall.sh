pipenv uninstall --all
rm -rf src/jupyter-kernel-test/pip-wheel-metadata
pipenv install --dev
python -m zsh_jupyter_kernel.install --sys-prefix
