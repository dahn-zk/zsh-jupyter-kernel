from setuptools import setup
import re

from zsh_kernel import __version__

with open('README.md') as f:
    long_description = re.sub(r'.*example screenshot.*', '', f.read()) # [1]
long_description_content_type = "text/markdown"

setup(
    name = 'zsh_kernel',
    version = __version__,
    packages = ['zsh_kernel'],
    description = 'Z shell kernel for Jupyter',
    long_description = long_description,
    long_description_content_type = long_description_content_type,
    author = 'Dan Oak',
    author_email = 'danylo.dubinin@gmail.com',
    url = 'https://github.com/danylo-dubinin/zsh-jupyter-kernel',
    install_requires = [
        'jupyter_client',
        'IPython',
        'ipykernel',
    ],
    package_data = {
        'zsh_kernel': [
            'banner.txt',
        ],
    },
    license = 'GPL-3.0',
    classifiers = [
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Other Scripting Engines',
        'Topic :: System :: Shells',
    ],
    keywords = [
        'jupyter', 'ipython', 'zsh', 'shell', 'kernel',
    ],
)

# Reference
# https://packaging.python.org/tutorials/packaging-projects/
# [1]: Image references are not handled by PyPi as for examle on GitHub are.
