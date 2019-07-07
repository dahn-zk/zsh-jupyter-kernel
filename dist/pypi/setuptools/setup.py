from setuptools import setup
from os.path import realpath

# noinspection PyUnresolvedReferences
from zsh_jupyter_kernel.config import config # [pycharm-unresolved]

setup(
    name = config['name'],
    version = config['version'],
    packages = [config['module']],
    description = config['description'],
    long_description = config['long_description']['md_without_images']['content'], # [1]
    long_description_content_type = config['long_description']['md_without_images']['type'],
    author = config['author'],
    author_email = config['author_email'],
    url = config['github_url'],
    install_requires = config['requirements'],
    package_data = {
        config['module']: config['non_python_files'],
    },
    license = config['license'],
    classifiers = [
        'Development Status :: 3 - Alpha',
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
    keywords = config['keywords'],
    python_requires = config['python_version'],
)

# Reference
# https://packaging.python.org/tutorials/packaging-projects/
# [1]: Image references are not handled by PyPi as for example on GitHub are.
# [pycharm-unresolved]: In PyCharm shows 'Unresolved' warning for some reason. No idea why.
