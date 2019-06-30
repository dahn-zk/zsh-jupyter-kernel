"""Configuration"""

import sys
import subprocess

from os.path import join, dirname, realpath

from . import __version__

conf = {
    'module_dir': dirname(realpath(__file__)),
    'project_url': 'https://github.com/danylo-dubinin/zsh-jupyter-kernel',
    'git_revision_hash': subprocess
        .check_output(['git', 'rev-parse', 'HEAD'])
        .decode()
        .strip(),
}

conf.update({
    'logfile': join(conf['module_dir'], 'kernel.log'),
    'logging_formatter': # [logging]
        '%(asctime)s | %(name)-10s | %(levelname)-6s | %(message)s',
    'log_level': "INFO",
    'pexpect': { # [pexpect-spawn]
        'cmd': 'zsh', 'args': [
            '-o', 'INTERACTIVE',
            '-o', 'NO_ZLE',
            '-o', 'NO_BEEP',
            '-o', 'TRANSIENT_RPROMPT',
            '-o', 'NO_PROMPT_CR',
            '-o', 'INTERACTIVE_COMMENTS',
            # '-o', 'XTRACE',
            # '-o', 'NO_RCS',
        ], # [zsh-options]
        'encoding': 'utf-8',
        'codec_errors': 'replace', # [codecs]
        'timeout': 5,
        'logfile': join(conf['module_dir'], 'pexpect.log'),
    },
    'kernel': {
        'spec': { # [kernel-specs]
            "argv": [
                sys.executable,
                    "-m", 'zsh_kernel',
                        "-f", "{connection_file}",
            ],
            "display_name": "Z shell",
            "language": "zsh",
            # "interrupt_mode": "message", # [interrupt]
            "interrupt_mode": "signal",
        },
        'code_completness': {'cmd': "zsh -nc '{}'"},
        'code_inspection': {'cmd': r"""zsh -c 'man -P "col -b" \\'{}\\''"""},
        'code_completion': {'cmd': conf['module_dir'] + "/capture.zsh '{}'"},
            # https://github.com/danylo-dubinin/zsh-capture-completion
            # Thanks to https://github.com/Valodim/zsh-capture-completion
    },
})

conf['kernel']['info'] = {
    'protocol_version': '5.3',
    'implementation': "ZshKernel",
    'implementation_version': __version__,
    'language_info': {
        'name': 'zsh',
        'version': '5.7.1',
        'mimetype': 'text/x-zsh',
        'file_extension': '.zsh',
        'pygments_lexer': 'shell',
        'codemirror_mode': 'shell',
        'help_links': [
            {
                'text': 'Intro',
                'url': f'{conf["project_url"]}'
                    + f'/blob/{conf["git_revision_hash"]}/README.md',
            },
        ],
    },
}
with open(join(conf['module_dir'], 'banner.txt'), 'r') as f:
    conf['kernel']['info']['banner'] = f.read()

# ## Reference
# [pexpect-spawn]: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
# [codecs]: https://docs.python.org/3/library/codecs.html
# [logging]: https://docs.python-guide.org/writing/logging/
# [zsh-options]: https://linux.die.net/man/1/zshoptions
#
# [interrupt]: https://jupyter-client.readthedocs.io/en/latest/messaging.html#kernel-interrupt
# Interrupt by message does not work now but works by signal. This is
# confusing as hell to me as previously it was not working. Whatever...
#
# [kernel-specs]: https://jupyter-client.readthedocs.io/en/latest/kernels.html#kernelspecs
