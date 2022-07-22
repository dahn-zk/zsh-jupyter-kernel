__all__ = ['config']

import json
import re
import sys
from os import makedirs
from os.path import join, dirname, realpath
from typing import Dict, Any

config : Dict[str, Any] = {}

config.update({
    'logging_enabled': False,
})

config.update({
    'module_dir': dirname(realpath(__file__)),
})

version : str
with open(join(config['module_dir'], 'version')) as f:
    version = f.read()

config.update({
    'name': 'zsh-jupyter-kernel',
    'module': 'zsh_jupyter_kernel',
    'version': version,
    'description': 'Z shell kernel for Jupyter',
    'author': 'dan oak',
    'author_email': 'curly-brace-17@protonmail.com',
    'license': '',
    'github_url': 'https://github.com/dany-oak/zsh-jupyter-kernel',
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
        'IPython',
            # only for tempdir
        'pexpect',
            # Spawning and interacting with Zsh pseudo terminal
    ],
})

config.update({
    'python_version': '>=3.10',
    # 'git_revision_hash': subprocess
    #     .check_output(['git', 'rev-parse', 'HEAD'])
    #     .decode()
    #     .strip(), # git-config fails in a distributed package
    'tests_suffix': "_test.py",
    'log_dir': realpath(join(dirname(realpath(__file__)), 'log')),
})

config.update({
    'readme': realpath(join(config['module_dir'], 'README.md')),
})


config['long_description'] = {}
with open(join(config['module_dir'], config['readme'])) as f:
    readme_md = f.read()
    config['long_description']['md'] = {
        'content': readme_md,
        'type': 'text/markdown',
    }
    config['long_description']['md_without_images'] = {
        'content': re.sub(r'\n.*!\[.*screenshot.*\].*\n', '', readme_md),
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
        'spec': { # [kernel-specs]
            "argv": [
                sys.executable,
                    "-m", 'zsh_jupyter_kernel',
                        "-f", "{connection_file}",
            ],
            "display_name": "Z shell",
            "language": "zsh",
            # "interrupt_mode": "message", # [interrupt]
            "interrupt_mode": "signal",
        },
        'code_completness': {'cmd': "zsh -nc '{}'"},
        'code_inspection': {'cmd': r"""zsh -c 'man -P "col -b" \'{}\\''"""},
        'code_completion': {'cmd': config['module_dir'] + "/capture.zsh '{}'"},
            # https://github.com/danylo-dubinin/zsh-capture-completion
            # Thanks to https://github.com/Valodim/zsh-capture-completion
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
        # 'help_links': [
        #     {
        #         'text': 'Intro',
        #         'url': f'{config["github_url"]}/blob/{config["git_revision_hash"]}/README.md',
        #     },
        # ], # git-config fails in a distributed package
    },
}
with open(join(config['module_dir'], 'banner.txt'), 'r') as f:
    config['kernel']['info']['banner'] = f.read()

if __name__ == '__main__':
    print(json.dumps(config, indent = 4))

