from ipykernel.kernelbase import Kernel
import os
import io
import pexpect
import logging as log
from collections import OrderedDict
import sys
import time
import signal
from tornado import gen, ioloop
import zmq

from .conf import conf
from . import __version__

class ZshKernel (Kernel):

    implementation = "ZshKernel"
    implementation_version = __version__
    protocol_version = conf['kernel']['protocol_version']
    with open(os.path.join(conf['module_root'], 'banner.txt'), 'r') as f:
        banner = f.read()
    language_info = {
        'name': 'zsh',
        'version': '5.3',
        'mimetype': 'text/x-zsh',
        'file_extension': '.zsh',
        'pygments_lexer': 'shell',
        'codemirror_mode': 'shell',
    }

    child : pexpect.spawn # [spawn]

    prompts = OrderedDict([
        ('PS1', 'PEXPECT_PS1 > '),
        ('PS2', 'PEXPECT_PS2 + '),
        ('PS3', 'PEXPECT_PS3 : '),
    ]) # [zsh-prompts]

    pexpect_logfile : io.IOBase = None

    def _init_log_(self):
        handler = log.handlers.WatchedFileHandler(conf['logfile'])
        formatter = log.Formatter(conf['logging_formatter'])
        handler.setFormatter(formatter)
        root = log.getLogger()
        root.setLevel(conf['log_level'])
        root.addHandler(handler)

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
        log.debug("Reinitializing required parameters and functions")
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
        log.debug(f"Initializing using {conf}")
        self._init_spawn_()
        self._init_zsh_()
        log.debug("Initialized")

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
        log.debug("info request sent: %s", msg)

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
                log.debug("code: %s", line)
                self.child.sendline(line)
                actual = self.child.expect_exact(
                    list(self.prompts.values()) + [os.linesep]
                )
                if actual == 0:
                    log.debug(f"output: {self.child.before}")
                    if not silent:
                        self.send_response(self.iopub_socket, 'stream', {
                            'name': 'stdout',
                            'text': self.child.before,
                        })
                else:
                    while actual == 3:
                        log.debug(f"output: {self.child.before}")
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
            log.info("Interrupted by user")
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
            log.exception("Value Error")
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
            log.exception("Timeout")
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
            log.exception("End of file")
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

        log.info(f"Success {self.execution_count}")
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

    # Copy-pasted from kernelbase.shutdown_request to implement
    # interrupt_request - new message in messaging specification 5.3
    @gen.coroutine
    def interrupt_request(self, stream, ident, parent):
        content = yield gen.maybe_future(self.do_interrupt())
        self.session.send(stream, u'interrupt_reply', content, parent, ident=ident)
        # same content, but different msg_id for broadcasting on IOPub
        self._shutdown_message = self.session.msg(u'interrupt_reply',
                                                  content, parent
        )

        self._at_shutdown()
        # call sys.exit after a short delay
        loop = ioloop.IOLoop.current()
        loop.add_timeout(time.time()+0.1, loop.stop)

    def do_interrupt(self):
        self.child.kill(signal.SIGQUIT) # [pexpect-kill][os-kill][signal]
        log.debug("interrupted by SIGQUIT")
        return {'status': 'ok'}

    # Copy-pasted from kernelbase to patch it with support of interrupt request
    @gen.coroutine
    def dispatch_control(self, msg):
        """dispatch control requests"""
        idents, msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.deserialize(msg, content=True, copy=False)
        except:
            self.log.error("Invalid Control Message", exc_info=True)
            return

        self.log.debug("Control received: %s", msg)

        # Set the parent message for side effects.
        self.set_parent(idents, msg)
        self._publish_status(u'busy')
        if self._aborting:
            self._send_abort_reply(self.control_stream, msg, idents)
            self._publish_status(u'idle')
            return

        header = msg['header']
        msg_type = header['msg_type']

        handler = self.control_handlers.get(msg_type, None)
        if handler is None:
            self.log.error("UNKNOWN CONTROL MESSAGE TYPE: %r", msg_type)
        # <> patched part
        elif msg_type == 'interrupt_request':
            try:
                yield gen.maybe_future(self.interrupt_request(self.control_stream, idents, msg))
            except Exception:
                self.log.error("Exception in control handler:", exc_info=True)
        # </>
        else:
            try:
                yield gen.maybe_future(handler(self.control_stream, idents, msg))
            except Exception:
                self.log.error("Exception in control handler:", exc_info=True)

        sys.stdout.flush()
        sys.stderr.flush()
        self._publish_status(u'idle')
        # flush to ensure reply is sent
        self.control_stream.flush(zmq.POLLOUT)

# Reference
# [spawn]: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
# [zsh-prompts]: https://jlk.fjfi.cvut.cz/arch/manpages/man/zshparam.1#PARAMETERS_USED_BY_THE_SHELL
# [1]: # https://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.expect
# [traceback]: https://docs.python.org/3/library/traceback.html#traceback.extract_tb
# [zsh-functions]: http://zsh.sourceforge.net/Doc/Release/Functions.html
# [zsh-bracketed-paste]: https://archive.zhimingwang.org/blog/2015-09-21-zsh-51-and-bracketed-paste.html
# [pexpect-kill]: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.kill
# [os-kill]: https://docs.python.org/3/library/os.html#os.kill
# [signal]: `man signal`
