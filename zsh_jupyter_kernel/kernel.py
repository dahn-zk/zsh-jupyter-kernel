import json
import logging
import logging.handlers
import os
import re
from collections import OrderedDict as odict
from typing import IO

import pexpect
from ipykernel.kernelbase import Kernel

from .config import config
from .fun import find_word_at_pos

class ZshKernel(Kernel):
    implementation = config["kernel"]["info"]["implementation"]
    implementation_version = config["kernel"]["info"]["implementation_version"]
    banner = config["kernel"]["info"]["banner"]
    language_info = config["kernel"]["info"]["language_info"]
    
    protocol_version = config["kernel"]["info"]["protocol_version"]
    
    p: pexpect.spawn  # [spawn]
    
    ps = odict([
        ("PS1", "PEXPECT_PS1 > "),
        ("PS2", "PEXPECT_PS2 + "),
        ("PS3", "PEXPECT_PS3 : "),
    ])
    ps_re = odict([
        ("PS1", "^PEXPECT_PS1 > "),
        ("PS2", r"^PEXPECT_PS2 \+ "),
        ("PS3", "^PEXPECT_PS3 : "),
    ])
    
    pexpect_logfile: IO = None
    
    log_enabled: bool
    
    def _init_log_(self, **kwargs):
        self.log_enabled = config["logging_enabled"]
        if self.log_enabled:
            handler = logging.handlers.WatchedFileHandler(config["logging_file_path"])
            formatter = logging.Formatter(config["logging_formatter"])
            handler.setFormatter(formatter)
            self.log.setLevel(config["logging_level"])
            self.log.addHandler(handler)
    
    def _init_spawn_(self, **kwargs):
        args = [
            "-o", "INTERACTIVE",  # just to make sure
            "-o", "NO_ZLE",  # no need for zsh line editor
            "-o", "NO_BEEP",
            "-o", "TRANSIENT_RPROMPT",
            "-o", "NO_PROMPT_CR",
            "-o", "INTERACTIVE_COMMENTS",
        ]  # [zsh-options]
        if not kwargs.get("rcs", False):
            args.extend(["-o", "NO_RCS"])
        if self.log_enabled:
            self.pexpect_logfile = open(config["pexpect"]["logging_file_path"], "a")
        self.p = pexpect.spawn(
            "zsh",
            args,
            echo = False,
            encoding = config["pexpect"]["encoding"],
            codec_errors = config["pexpect"]["codec_errors"],
            timeout = config["pexpect"]["timeout"],
            logfile = self.pexpect_logfile,
        )
    
    def _init_zsh_(self, **kwargs):
        init_cmds = [
            *config["zsh"]["init_cmds"],
            *map(lambda kv: "{}='{}'".format(*kv), self.ps.items()),
        ]
        self.p.sendline("; ".join(init_cmds))
        self.p.expect_exact(self.ps["PS1"])
        config_cmds = [
            *config["zsh"]["config_cmds"],
        ]
        self.p.sendline("; ".join(config_cmds))
        self.p.expect_exact(self.ps["PS1"])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_log_()
        if self.log_enabled:
            self.log.debug("initializing %s", json.dumps(config, indent = 4))
        self._init_spawn_()
        self._init_zsh_(**kwargs)
        # self.p.sendline("tty")
        # self.p.expect_exact(self.ps['PS1'])
        if self.log_enabled:
            self.log.debug("initialized")
        if self.log_enabled:
            self.log.debug("kwargs:" + str(kwargs))
    
    def __del__(self):
        try:
            self.pexpect_logfile.close()
        except AttributeError:
            pass
    
    def kernel_info_request(self, stream, ident, parent):
        content = {"status": "ok"}
        content.update(self.kernel_info)
        content.update({"protocol_version": self.protocol_version})
        msg = self.session.send(stream, "kernel_info_reply", content, parent, ident)
        if self.log_enabled:
            self.log.debug("info request sent: %s", msg)
    
    def _execute_line(self, line, silent):
        if self.log_enabled:
            self.log.debug("code: %s", line)
        self.p.sendline(line)
        actual = self.p.expect(list(self.ps_re.values()) + [os.linesep])
        if actual == 0:
            if self.log_enabled:
                self.log.debug(f"got PS1. output: {self.p.before}")
            if not silent:
                if len(self.p.before) != 0:
                    self.send_response(self.iopub_socket,
                        "stream", {"name": "stdout", "text": self.p.before})
        else:
            while actual == 3:
                if self.log_enabled:
                    self.log.debug(f"got linesep. output: {self.p.before}")
                if not silent:
                    self.send_response(self.iopub_socket,
                        "stream", {"name": "stdout", "text": self.p.before + os.linesep})
                actual = self.p.expect(list(self.ps_re.values()) + [os.linesep])
        return actual
    
    def _execute_code(self, code, silent):
        actual = None
        for line in code.splitlines():
            actual = self._execute_line(line, silent)
        if self.log_enabled:
            self.log.debug(f"executed all lines. actual: {actual}")
        if actual in [1, 2]:
            self.p.sendline()
            # "flushing"
            actual = self.p.expect(list(self.ps_re.values()))
            while actual != 0:
                actual = self.p.expect(list(self.ps_re.values()) + [re.compile(".*")])
            if not silent:
                self.send_response(self.iopub_socket,
                    "stream", {"name": "stdout", "text": self.p.before})
            raise ValueError("Continuation or selection prompts are not handled yet")
    
    def _get_error_response(self, exc):
        return {
            "execution_count": self.execution_count,
            "ename": exc.__class__.__name__,
            "evalue": exc.__class__.__name__,
            "traceback": [],
            # 'traceback': traceback.extract_stack(exc),
        }
    
    def do_execute(self, code: str, silent: bool, store_history = True,
            user_expressions: dict = None, **kwargs):
        try:
            self._execute_code(code, silent)
        except KeyboardInterrupt as exc:
            if self.log_enabled: self.log.debug("interrupted by user")
            self.p.sendintr()
            self.p.expect_exact(self.ps["PS1"])
            if not silent:
                self.send_response(self.iopub_socket, "stream",
                    {"name": "stdout", "text": self.p.before})
            error_response = self._get_error_response(exc)
            return {"status": "error", **error_response}
        except ValueError as exc:
            if self.log_enabled: self.log.exception("value error")
            error_response = self._get_error_response(exc)
            self.send_response(self.iopub_socket, "error", error_response)
            return {"status": "error", **error_response}
        except pexpect.TIMEOUT as exc:
            if self.log_enabled: self.log.exception("timeout")
            error_response = self._get_error_response(exc)
            self.send_response(self.iopub_socket, "error", error_response)
            return {"status": "error", **error_response}
        except pexpect.EOF as exc:
            if self.log_enabled: self.log.exception("end of file")
            error_response = self._get_error_response(exc)
            self.send_response(self.iopub_socket, "error", error_response)
            return {"status": "error", **error_response}
        
        if self.log_enabled: self.log.debug(f"success {self.execution_count}")
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }
    
    def do_is_complete(self, code: str):
        (_, exitstatus) = pexpect.run(
            "zsh -nc '{}'".format(code),
            withexitstatus = True,
        )
        if exitstatus == 0:
            return {"status": "complete"}
        elif exitstatus == 1:
            return {"status": "incomplete"}
    
    def do_inspect(self, code: str, cursor_pos: int, detail_level: int = 0,
            omit_sections = ()):
        word = find_word_at_pos(code, cursor_pos)
        if self.log_enabled:
            self.log.debug("inspecting: %s", word)
        cman = f"man --pager ul {word}"
        res = pexpect.run(cman).decode()
        return {
            "status": "ok",
            "found": True,
            "data": {"text/plain": res},
            "metadata": {},
        }
    
    @staticmethod
    def _parse_completee(code: str, cursor_pos: int) -> tuple:
        context = code[:cursor_pos]
        match = re.search(r"\S+$", context)
        if not match:
            match = re.search(r"\w+$", context)
        if not match:
            completee = ""
        else:
            completee = match.group(0)
        cursor_start = cursor_pos - len(completee)
        cursor_end = cursor_pos
        return context, completee, cursor_start, cursor_end
    
    def do_complete(self, code: str, cursor_pos: int):
        if self.log_enabled:
            self.log.debug("received code to complete:\n%s", code)
        if self.log_enabled:
            self.log.debug("cursor_pos=%s", cursor_pos)
        (context, completee, cursor_start, cursor_end) = \
            self._parse_completee(code, cursor_pos)
        if self.log_enabled:
            self.log.debug("parsed completee: %s",
                (context, completee, cursor_start, cursor_end))
        completion_cmd = config["kernel"]["code_completion"]["cmd"].format(context)
        self.p.sendline(completion_cmd)
        self.p.expect_exact(self.ps["PS1"])
        raw_completions = self.p.before.strip()
        if self.log_enabled:
            self.log.debug("got completions:\n%s", raw_completions)
        completions = list(filter(None, raw_completions.splitlines()))
        if self.log_enabled:
            self.log.debug("array of completions: %s", completions)
        matches_data = list(
            map(lambda x: x.split(" -- "), completions)
        )  # [match, description]
        if self.log_enabled:
            self.log.debug("processed matches: %s", matches_data)
        return {
            "status": "ok",
            "matches": [x[0] for x in matches_data],
            "cursor_start": cursor_start,
            "cursor_end": cursor_end,
            "metadata": {},
        }
    
    def send_response(self, stream, msg_or_type, content = None, ident = None,
            buffers = None, track = False, header = None, metadata = None, channel = None):
        if self.log_enabled:
            self.log.debug("sending response: %s", msg_or_type)
        super().send_response(stream, msg_or_type, content, ident, buffers, track,
            header, metadata, channel)
