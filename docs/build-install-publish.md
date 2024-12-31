https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools

```zsh
python -m pip install setuptools
python -m pip install build
python -m pip install twine

python -m build

twine upload --repository testpypi dist/*

pip install --index-url https://test.pypi.org/simple/ zsh-jupyter-kernel
python -m zsh_jupyter_kernel.install --sys-prefix

#version=`cat version`
twine upload \
  dist/zsh-jupyter-kernel-$version.tar.gz \
  dist/zsh_jupyter_kernel-$version-py3-none-any.whl
```
