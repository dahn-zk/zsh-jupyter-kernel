# configuration, packaging and distribution tools

## pypi

### setuptools

to build a distribution:

change the working directory to `dist/pypi/setuptools`.

```zsh
python setup.py sdist bdist_wheel
```

then to test it, upload it to testpypi:

```zsh
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

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
