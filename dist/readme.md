# Configuration, packaging and distribution tools

## PyPi

### setuptools

To build a distribution:

```zsh
python setup.py sdist bdist_wheel
```

Then to test it, upload it to TestPyPi:
```zsh
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

And run in separate Pipenv:
```zsh
pipenv install notebook

version=x.y # set version
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  zsh-jupyter-kernel==$version

python -m zsh_jupyter_kernel.install --sys-prefix
```

To upload to production PyPi:
```zsh
twine upload \
  dist/zsh-jupyter-kernel-$version.tar.gz \
  dist/zsh_jupyter_kernel-$version-py3-none-any.whl
```
