https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools

```zsh
python -m pip install setuptools
python -m pip install build
python -m pip install twine

python -m build

twine upload --repository testpypi dist/*

and run in a separate window and a separate directory to test the
installation from testpypi:

```zsh
pipenv install --python=3.10 notebook
pipenv shell
pip install --index-url https://test.pypi.org/simple/ zsh-jupyter-kernel
python -m zsh_jupyter_kernel.install --sys-prefix
```

to upload to production pypi set the version and execute:

```zsh
version=`cat version`
twine upload \
  dist/zsh-jupyter-kernel-$version.tar.gz \
  dist/zsh_jupyter_kernel-$version-py3-none-any.whl
```
