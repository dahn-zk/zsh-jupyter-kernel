# Configuration, packaging and distribution tools

## PyPi

### setuptools

To build a distribution:

Change the working directory to `dist/pypi/setuptools`.

```zsh
python setup.py sdist bdist_wheel
```

Then to test it, upload it to TestPyPi:
```zsh
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

And run in a separate window and a separate directory to test the 
installation from TestPyPi:
```zsh
pipenv install --python=3 

pipenv install notebook

pipenv shell

pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  zsh-jupyter-kernel

python -m zsh_jupyter_kernel.install --sys-prefix
```

To upload to production PyPi set the version and execute:
```zsh
version=
twine upload \
  dist/zsh-jupyter-kernel-$version.tar.gz \
  dist/zsh_jupyter_kernel-$version-py3-none-any.whl
```
