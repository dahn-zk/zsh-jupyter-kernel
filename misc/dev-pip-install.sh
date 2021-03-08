# deactivate conda environment if any
conda deactivate
# create virtual environment
python3 -m venv venv
# activate it
. ./venv/bin/activate
# install jupyter dependencies and notebook
pip install jupyter_protocol jupyter_kernel_test jupyter-console notebook jupyterlab
# install zsh kernel as editable package
pip install -e ./dist/pypi/setuptools
# install the kernel itself
python -m zsh_jupyter_kernel.install --sys-prefix
# quick test
jupyter console --kernel=zsh
