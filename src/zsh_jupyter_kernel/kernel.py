from ipykernel.kernelbase import Kernel
import os
import io
import pexpect
import logging
from collections import OrderedDict
import json
import re

from .config import config

class ZshKernel (Kernel):

    implementation         = config['kernel']['info']['implementation']
    implementation_version = config['kernel']['info']['implementation_version']
    protocol_version       = config['kernel']['info']['protocol_version']
    banner                 = config['kernel']['info']['banner']
    language_info          = config['kernel']['info']['language_info']

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
        handler = logging.handlers.WatchedFileHandler(config['logfile'])
        formatter = logging.Formatter(config['logging_formatter'])
        handler.setFormatter(formatter)
        self.log.setLevel(config['log_level'])
        self.log.addHandler(handler)

    def _init_spawn_(self):
        self.pexpect_logfile = open(config['pexpect']['logfile'], 'a')
        self.child = pexpect.spawn(
            config['pexpect']['cmd'], config['pexpect']['args'],
            echo = False,
            encoding = config['pexpect']['encoding'],
            codec_errors = config['pexpect']['codec_errors'],
            timeout = config['pexpect']['timeout'],
            logfile = self.pexpect_logfile,
        )

    def _init_zsh_(self):
        init_cmds = [
            *config['zsh']['init_cmds'],
            *map(lambda kv: "{}='{}'".format(*kv), self.prompts.items()),
        ]
        self.child.sendline("; ".join(init_cmds))
        self.child.expect_exact(self.prompts['PS1'])
        config_cmds = [
            *config['zsh']['config_cmds'],
        ]
        self.child.sendline("; ".join(config_cmds))
        self.child.expect_exact(self.prompts['PS1'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_log_()
        self.log.debug("Initializing %s", self._json_(config))
        self._init_spawn_()
        self._init_zsh_()
        self.child.sendline("tty")
        self.child.expect_exact(self.prompts['PS1'])
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
            code_lines : list = code.splitlines()
            actual = None
            for line in code_lines:
                self.log.debug("code: %s", line)
                self.child.sendline(line)
                actual = self.child.expect_exact(
                    list(self.prompts.values()) + [os.linesep]
                )
                if actual == 0:
                    self.log.debug(f"got PS1. output: {self.child.before}")
                    if not silent:
                        if len(self.child.before) != 0:
                            self.send_response(self.iopub_socket, 'stream', {
                                'name': 'stdout',
                                'text': self.child.before,
                            })
                else:
                    while actual == 3:
                        self.log.debug(f"got linesep. output: {self.child.before}")
                        if not silent:
                            self.send_response(self.iopub_socket, 'stream', {
                                'name': 'stdout',
                                'text': self.child.before + os.linesep,
                            })
                        actual = self.child.expect_exact(
                            list(self.prompts.values()) + [os.linesep]
                        )
            self.log.debug(f"executed all lines. actual: {actual}")
            if actual in [1, 2]:
                self.child.sendline()
                # "flushing"
                actual = self.child.expect_exact(self.prompts.values())
                while actual != 0:
                    actual = self.child.expect(
                        self.child.expect_exact(self.prompts.values()) +
                        [re.compile(".*")])
                if not silent:
                    self.send_response(self.iopub_socket, 'stream', {
                        'name': 'stdout',
                        'text': self.child.before,
                    })
                raise ValueError(
                    "Continuation or selection prompts are not handled yet"
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
        (_, exitstatus) = pexpect.run(
            config['kernel']['code_completness']['cmd'].format(code),
            withexitstatus = True,
        )
        if exitstatus == 0:
            return {
                'status': 'complete',
            }
        elif exitstatus == 1:
            return {
                'status': 'incomplete',
            }

    def do_inspect(self, code : str, cursor_pos : int, detail_level : int = 0):
        self.log.debug("Received code to inspect:\n%s", code)
        self.log.debug("cursor_pos=%s, detail_level=%d",
            cursor_pos, detail_level,
        )
        line = code # TODO: select line where the cursor is
        self.log.debug("Inspecting: %s", line)

        man_page = pexpect.run(
            config['kernel']['code_inspection']['cmd'].format(line),
        ).decode()
        return {
            'status': 'ok',
            'found': True,
            'data': {
                'text/plain': man_page,
            },
            'metadata': {},
        }

    def parse_completee(self, code : str, cursor_pos : int) -> tuple:
            # (context, completee, cursor_start, cursor_end)
        context = code[:cursor_pos]
        match = re.search(r'\S+$', context)
        if not match:
            match = re.search(r'\w+$', context)
        if not match:
            completee = ''
        else:
            completee = match.group(0)
        cursor_start = cursor_pos - len(completee)
        cursor_end = cursor_pos
        return (context, completee, cursor_start, cursor_end)

    def do_complete(self, code : str, cursor_pos : int):
        self.log.debug("Received code to complete:\n%s", code)
        self.log.debug("cursor_pos=%s", cursor_pos)
        (context, completee, cursor_start, cursor_end) = \
            self.parse_completee(code, cursor_pos)
        self.log.debug("Parsed completee: %s",
            (context, completee, cursor_start, cursor_end))
        completion_cmd = config['kernel']['code_completion']['cmd'] \
            .format(context)
        self.child.sendline(completion_cmd)
        self.child.expect_exact(self.prompts.values())
        raw_completions = self.child.before
        self.log.debug("Got completions:\n%s", raw_completions)
        completions = list(filter(None, raw_completions.strip().splitlines()))
        self.log.debug("Array of completions: %s", completions)
        matches_data = list(map(lambda x: x.split(' -- '), completions))
            # [match, description]
        self.log.debug("Processed matches: %s", matches_data)
        return {
            'status': 'ok',
            'matches': [x[0] for x in matches_data],
            'cursor_start' : cursor_start,
            'cursor_end' : cursor_end,
            'metadata' : {},
        }

# Reference
# [spawn]: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
# [zsh-prompts]: https://jlk.fjfi.cvut.cz/arch/manpages/man/zshparam.1#PARAMETERS_USED_BY_THE_SHELL
# [1]: # https://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.expect
# [traceback]: https://docs.python.org/3/library/traceback.html#traceback.extract_tb
