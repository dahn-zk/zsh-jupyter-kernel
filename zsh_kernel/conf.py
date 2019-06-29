"""Configuration"""

import sys

from os.path import join, dirname, realpath

dirname = dirname(realpath(__file__))

conf = {
    'module_root': dirname,
    'logfile': join(dirname, 'kernel.log'),
    'logging_formatter': # [logging]
        '%(asctime)s | %(name)-10s | %(levelname)-6s | %(message)s',
    'log_level': "DEBUG",
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
        'logfile': join(dirname, 'pexpect.log'),
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
            "interrupt_mode": "message", # [interrupt]
        },
        'protocol_version': '5.3',
        'code_completness': {'cmd': "zsh -nc '{}'"},
    }
}

# ## Reference
# [pexpect-spawn]: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
# [codecs]: https://docs.python.org/3/library/codecs.html
# [logging]: https://docs.python-guide.org/writing/logging/
# [zsh-options]: https://linux.die.net/man/1/zshoptions
# [interrupt]: https://jupyter-client.readthedocs.io/en/latest/messaging.html#kernel-interrupt
# [kernel-specs]: https://jupyter-client.readthedocs.io/en/latest/kernels.html#kernelspecs
