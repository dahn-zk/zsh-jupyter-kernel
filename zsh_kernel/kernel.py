from ipykernel.kernelbase import Kernel
import os
import io
import pexpect
import logging
from collections import OrderedDict
import json

from .conf import conf

class ZshKernel (Kernel):

    implementation         = conf['kernel']['info']['implementation']
    implementation_version = conf['kernel']['info']['implementation_version']
    protocol_version       = conf['kernel']['info']['protocol_version']
    banner                 = conf['kernel']['info']['banner']
    language_info          = conf['kernel']['info']['language_info']

    child : pexpect.spawn # [spawn]

    prompts = OrderedDict([
        ('PS1', 'PEXPECT_PS1 > '),
        ('PS2', 'PEXPECT_PS2 + '),
        ('PS3', 'PEXPECT_PS3 : '),
    ]) # [zsh-prompts]

    pexpect_logfile : io.IOBase = None

    def _json_(self, d : dict):
        return json.dumps(d, indent = 4)

    def _init_log_(self):
        handler = logging.handlers.WatchedFileHandler(conf['logfile'])
        formatter = logging.Formatter(conf['logging_formatter'])
        handler.setFormatter(formatter)
        self.log.setLevel(conf['log_level'])
        self.log.addHandler(handler)

    def _init_spawn_(self):
        self.pexpect_logfile = open(conf['pexpect']['logfile'], 'a')
        self.child = pexpect.spawn(
            conf['pexpect']['cmd'], conf['pexpect']['args'],
            echo = False,
            encoding = conf['pexpect']['encoding'],
            codec_errors = conf['pexpect']['codec_errors'],
            timeout = conf['pexpect']['timeout'],
            logfile = self.pexpect_logfile,
        )

    def _init_zsh_(self):
        init_cmds = [
            "precmd() {}", # [zsh-functions]
            *map(lambda kv: "{}='{}'".format(*kv), self.prompts.items()),
            "unset zle_bracketed_paste", # [zsh-bracketed-paste]
        ]
        self.child.sendline("; ".join(init_cmds))
        self.child.expect_exact(self.prompts['PS1'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_log_()
        self.log.debug("Initializing %s", self._json_(conf))
        self._init_spawn_()
        self._init_zsh_()
        self.log.debug("Initialized")

    def __del__(self):
        try:
            self.pexpect_logfile.close()
        except AttributeError:
            pass

    def kernel_info_request(self, stream, ident, parent):
        content = {'status': 'ok'}
        content.update(self.kernel_info)
        content.update({'protocol_version': self.protocol_version})
        msg = self.session.send(stream, 'kernel_info_reply',
                                content, parent, ident)
        self.log.debug("info request sent: %s", msg)

    def do_execute(
        self,
        code : str,
        silent : bool,
        store_history = True,
        user_expressions : dict = None,
        allow_stdin = False,
    ):
        try:
            if not code:
                raise ValueError("No code given")

            code_lines : list = code.splitlines()
            for line in code_lines:
                self.log.debug("code: %s", line)
                self.child.sendline(line)
                actual = self.child.expect_exact(
                    list(self.prompts.values()) + [os.linesep]
                )
                if actual == 0:
                    self.log.debug(f"output: {self.child.before}")
                    if not silent:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stdout',
                            'text': self.child.before,
                        })
                else:
                    while actual == 3:
                        self.log.debug(f"output: {self.child.before}")
                        if not silent:
                            self.send_response(self.iopub_socket, 'stream', {
                                'name': 'stdout',
                                'text': self.child.before + os.linesep,
                            })
                        actual = self.child.expect_exact(
                            list(self.prompts.values()) + [os.linesep]
                        )
            if actual in [1, 2]:
                self.child.sendintr()
                self.child.expect_exact(self.prompts.values())
                raise ValueError(
                    "Continuation prompt found - command was incomplete"
                )

        except KeyboardInterrupt as e:
            self.log.debug("Interrupted by user")
            self.child.sendintr()
            self.child.expect_exact(self.prompts['PS1'])
            if not silent:
                self.send_response(self.iopub_socket, 'stream', {
                    'name': 'stdout',
                    'text': self.child.before,
                })
            return {
                'status': 'error',
                'execution_count': self.execution_count,
                'ename': e.__class__.__name__,
                'evalue': e.__class__.__name__,
                'traceback': [],
            }

        except ValueError as e:
            self.log.exception("Value Error")
            error_response = {
                'execution_count': self.execution_count,
                'ename': e.__class__.__name__,
                'evalue': e.__class__.__name__,
                'traceback': [],
                # 'traceback': traceback.extract_stack(e), # [traceback]
            }
            self.send_response(self.iopub_socket, 'error', error_response)
            return {
                'status': 'error',
                **error_response,
            }

        except pexpect.TIMEOUT as e:
            self.log.exception("Timeout")
            error_response = {
                'execution_count': self.execution_count,
                'ename': e.__class__.__name__,
                'evalue': e.__class__.__name__,
                'traceback': [],
                # 'traceback': traceback.extract_stack(e), # [traceback]
            }
            self.send_response(self.iopub_socket, 'error', error_response)
            return {
                'status': 'error',
                **error_response,
            }

        except pexpect.EOF as e:
            self.log.exception("End of file")
            error_response = {
                'execution_count': self.execution_count,
                'ename': e.__class__.__name__,
                'evalue': e.__class__.__name__,
                'traceback': [],
                # 'traceback': traceback.extract_stack(e), # [traceback]
            }
            self.send_response(self.iopub_socket, 'error', error_response)
            return {
                'status': 'error',
                **error_response,
            }

        self.log.debug(f"Success {self.execution_count}")
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

    def do_is_complete(self, code : str):
        # TODO: make it actually work for incomplete ones. exitstatus always 0
        try:
            (_, exitstatus) = pexpect.run(
                conf['kernel']['code_completness']['cmd'].format(code),
                withexitstatus = True,
            )
        except pexpect.ExceptionPexpect:
            return {
                'status': 'unknown',
            }
        if exitstatus == 0:
            return {
                'status': 'complete',
            }
        elif exitstatus == 1:
            return {
                'status': 'invalid',
            }

    def do_inspect(self, code : str, cursor_pos : int, detail_level : int = 0):
        self.log.debug("Received code to inspect:\n%s", code)
        self.log.debug("cursor_pos=%s, detail_level=%d",
            cursor_pos, detail_level,
        )
        line = code # TODO: select line where the cursor is
        self.log.debug("Inspecting: %s", line)

        man_page = pexpect.run(
            conf['kernel']['code_inspection']['cmd'].format(line),
        ).decode()
        return {
            'status': 'ok',
            'found': True,
            'data': {
                'text/plain': man_page,
            },
            'metadata': {},
        }

# Reference
# [spawn]: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
# [zsh-prompts]: https://jlk.fjfi.cvut.cz/arch/manpages/man/zshparam.1#PARAMETERS_USED_BY_THE_SHELL
# [1]: # https://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.expect
# [traceback]: https://docs.python.org/3/library/traceback.html#traceback.extract_tb
# [zsh-functions]: http://zsh.sourceforge.net/Doc/Release/Functions.html
# [zsh-bracketed-paste]: https://archive.zhimingwang.org/blog/2015-09-21-zsh-51-and-bracketed-paste.html
