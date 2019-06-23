from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name = 'zsh_kernel',
    version = '1.0',
    packages = ['zsh_kernel'],
    description = 'Z shell kernel for IPython',
    author = 'Dan Oak',
    author_email = 'danylo.dubinin@gmail.com',
    install_requires = [
        'jupyter_client',
        'IPython',
        'ipykernel',
    ],
)
