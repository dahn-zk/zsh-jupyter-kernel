# a list defining what symbols will be exported when `from <module> import *` is used
__all__ = ['config']

# note: this is not the cleanest way to manage a config, but i am lazy to reorganize it at this point

import json
import re
from os import makedirs
from os.path import join, dirname, realpath
from typing import Dict, Any

from .fun import get_canonical_dirname

config : Dict[str, Any] = {}
module_dirname = get_canonical_dirname(__file__)
version : str
with open(join(module_dirname, 'version')) as f:
    version = f.read()

config.update({
    'logging_enabled': False,
    'module_dir': module_dirname,
    'name': 'zsh-jupyter-kernel',
    'module': 'zsh_jupyter_kernel',
    'version': version,
    'description': 'Z shell kernel for Jupyter',
    'author': 'dan oak',
    'author_email': 'curly-brace-17@protonmail.com',
    'license': '',
    'github_url': 'https://github.com/dan-oak/zsh-jupyter-kernel',
    'keywords': [
        'jupyter',
        'ipython',
        'zsh',
        'shell',
        'kernel',
    ],
    'requirements': [
        'ipykernel',
            # kernelapp.IPKernelApp - Kernel launcher
            # kernelbase.Kernel - Convenient parent class with low level instrumentation
        'jupyter_client',
            # KernelSpecManager().install_kernel_spec
        'pexpect',
            # Spawning and interacting with Zsh pseudo terminal
    ],
    'python_version': '>=3.10',
    'log_dir': realpath(join(module_dirname, 'log')),
    'readme': realpath(join(module_dirname, 'README.md')),
})

config['long_description'] = {}
with open(join(module_dirname, config['readme'])) as f:
    readme_md = f.read()
    config['long_description']['md'] = {
        'content': readme_md,
        'type': 'text/markdown',
    }
    # replace github image links in the readme file to full url paths
    config['long_description']['md_with_github_image_links'] = {
        'content': re.sub(
            r'(!\[.*screenshot.*])\((.*)\)',
            r'\1(https://raw.githubusercontent.com/dan-oak/zsh-jupyter-kernel/master/\2)',
            readme_md),
        'type': 'text/markdown',
    }

config.update({
    # 'log_level': "DEBUG",
    'log_level': "INFO",
})
if config['logging_enabled']:
    config.update({
        'logfile': join(config['log_dir'], 'kernel.log'),
        'logging_formatter': # [logging]
            '%(asctime)s | %(name)-10s | %(levelname)-6s | %(message)s',
    })
    makedirs(dirname(config['logfile']), exist_ok = True)

config.update({
    'non_python_files': [
        'banner.txt',
        'capture.zsh',
        'README.md',
        'LICENSE.txt',
        'logo-32x32.png',
        'logo-64x64.png',
        'version',
    ],
    'pexpect': { # [pexpect-spawn]
        'encoding': 'utf-8',
        'codec_errors': 'replace', # [codecs]
        'timeout': None, # [pexpect-spawn-timeout]
        'logfile': join(config['log_dir'], 'pexpect.log'),
    },
    'zsh': {
        'init_cmds': [
            # "TERM=dumb",

            "autoload -Uz add-zsh-hook",
            "add-zsh-hook -D precmd \*",
            "add-zsh-hook -D preexec \*",
                # [zsh-hooks]

            "precmd() {}",
            "preexec() {}",
                # [zsh-functions]
        ],
        'config_cmds': [
            "unset zle_bracketed_paste", # [zsh-bracketed-paste]
            "zle_highlight=(none)", # https://linux.die.net/man/1/zshzle
        ],
    },
    'kernel': {
        'code_completion': {'cmd': module_dirname + "/capture.zsh '{}'"},
    },
})
if config['logging_enabled']:
    makedirs(dirname(config['pexpect']['logfile']), exist_ok = True)

config['kernel']['info'] = {
    'protocol_version': '5.3',
    'implementation': "ZshKernel",
    'implementation_version': config['version'],
    'language_info': {
        'name': 'zsh',
        'version': '5.7.1',
        'mimetype': 'text/x-zsh',
        'file_extension': '.zsh',
        'pygments_lexer': 'shell',
        'codemirror_mode': 'shell',
    },
}
with open(join(module_dirname, 'banner.txt'), 'r') as f:
    config['kernel']['info']['banner'] = f.read()

if __name__ == '__main__':
    print(json.dumps(config, indent = 4))

