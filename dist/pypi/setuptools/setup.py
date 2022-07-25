from setuptools import setup
from os.path import realpath

from zsh_jupyter_kernel.config import config

setup(
    name = config['name'],
    version = config['version'],
    packages = [config['module']],
    description = config['description'],
    long_description = config['long_description']['md_with_github_image_links']['content'], # [1]
    long_description_content_type = config['long_description']['md_with_github_image_links']['type'],
    author = config['author'],
    author_email = config['author_email'],
    url = config['github_url'],
    install_requires = config['requirements'],
    package_data = {
        config['module']: config['non_python_files'],
    },
    license = config['license'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Unix Shell',
        'Topic :: System :: Shells',
    ],
    keywords = config['keywords'],
    python_requires = config['python_version'],
)

# Reference
# https://packaging.python.org/tutorials/packaging-projects/
# [1]: Image references are not handled by PyPi as for example on GitHub are.
