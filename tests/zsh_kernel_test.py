import inspect
import queue
import unittest

import jupyter_client
import jupyter_client.utils

from . import msgspec_v5

TIMEOUT = 1

class zsh_kernel_tests(unittest.TestCase):
    km: jupyter_client.KernelManager
    kc: jupyter_client.BlockingKernelClient
    
    @classmethod
    def setUpClass(cls):
        cls.km, cls.kc = jupyter_client.manager.start_new_kernel(kernel_name = "zsh")
    
    @classmethod
    def tearDownClass(cls):
        cls.kc.stop_channels()
        cls.km.shutdown_kernel()
    
    def setUp(self):
        print()
    
    @staticmethod
    def run_sync(func):
        if inspect.iscoroutinefunction(func):
            return jupyter_client.utils.run_sync(func)
        return func
    
    def flush_channels(self):
        for channel in (self.kc.shell_channel, self.kc.iopub_channel):
            while True:
                try:
                    msg = self.run_sync(channel.get_msg)(timeout = 0.1)
                except TypeError:
                    msg = channel.get_msg(timeout = 0.1)
                except queue.Empty:
                    break
                else:
                    msgspec_v5.validate_message(msg)
    
    def execute(self, code: str, timeout = TIMEOUT, silent = False,
            store_history = True, stop_on_error = True):
        msg_id = self.kc.execute(code = code, silent = silent,
            store_history = store_history, stop_on_error = stop_on_error)
        reply = self.get_non_kernel_info_reply(timeout = timeout)
        msgspec_v5.validate_message(reply, "execute_reply", msg_id)
        busy_msg = self.run_sync(self.kc.iopub_channel.get_msg)(timeout = 1)
        msgspec_v5.validate_message(busy_msg, "status", msg_id)
        self.assertEqual(busy_msg["content"]["execution_state"], "busy")
        output_msgs = []
        while True:
            msg = self.run_sync(self.kc.iopub_channel.get_msg)(timeout = 0.1)
            msgspec_v5.validate_message(msg, msg["msg_type"], msg_id)
            if msg["msg_type"] == "status":
                self.assertEqual(msg["content"]["execution_state"], "idle")
                break
            elif msg["msg_type"] == "execute_input":
                self.assertEqual(msg["content"]["code"], code)
                continue
            output_msgs.append(msg)
        return reply, output_msgs
    
    def get_non_kernel_info_reply(self, timeout = None):
        while True:
            reply = self.kc.get_shell_msg(timeout = timeout)
            if reply["header"]["msg_type"] != "kernel_info_reply":
                return reply
    
    def check_is_complete(self, sample, status):
        msg_id = self.kc.is_complete(sample)
        reply = self.get_non_kernel_info_reply()
        msgspec_v5.validate_message(reply, "is_complete_reply", msg_id)
        if reply["content"]["status"] != status:
            msg = "for code sample\n  {!r}\nexpected {!r}, got {!r}."
            raise AssertionError(msg.format(sample, status, reply["content"]["status"]))
    
    def get_history(self, execute_first, timeout = TIMEOUT, **histargs):
        self.flush_channels()
        for code in execute_first:
            reply, output_msgs = self.execute(code)
        self.flush_channels()
        msg_id = self.kc.history(**histargs)
        reply = self.get_non_kernel_info_reply(timeout = timeout)
        msgspec_v5.validate_message(reply, "history_reply", msg_id)
        return reply
    
    def test_kernel_info(self):
        self.flush_channels()
        msg_id = self.kc.kernel_info()
        reply = self.kc.get_shell_msg(timeout = TIMEOUT)
        msgspec_v5.validate_message(reply, "kernel_info_reply", msg_id)
        self.assertEqual(reply["content"]["language_info"]["name"], "zsh")
        self.assertEqual(reply["content"]["language_info"]["file_extension"], ".zsh")
    
    def test_hello_world_stdout(self):
        self.flush_channels()
        reply, output_msgs = self.execute(code = "<<< 'hello, world'")
        self.assertEqual(reply["content"]["status"], "ok")
        self.assertGreaterEqual(len(output_msgs), 1)
        for msg in output_msgs:
            if (msg["msg_type"] == "stream") and (msg["content"]["name"] == "stdout"):
                self.assertIn("hello, world", msg["content"]["text"])
                break
        else:
            self.assertTrue(False, "expected one output message of type 'stream' and 'content.name'='stdout'")
    
    def test_hello_world_stderr(self):
        self.flush_channels()
        reply, output_msgs = self.execute(code = ">&2 print 'hello, world'")
        self.assertEqual(reply["content"]["status"], "ok")
        self.assertGreaterEqual(len(output_msgs), 1)
        for msg in output_msgs:
            if (msg["msg_type"] == "stream") and (msg["content"]["name"] == "stdout"):
                self.assertIn("hello, world", msg["content"]["text"])
                break
        else:
            self.assertTrue(False, "expected one output message of type 'stream' and 'content.name'='stdout'")
    
    def test_completion(self):
        samples = [
            {
                "text": "prin",
                "matches": [
                    "printafm",
                    "printf",
                    "printenv",
                    "printf",
                    "print",
                ],
            }
        ]
        for sample in samples:
            text = sample["text"]
            with self.subTest(text = text):
                msg_id = self.kc.complete(text)
                reply = self.get_non_kernel_info_reply(timeout = TIMEOUT)
                msgspec_v5.validate_message(reply, "complete_reply", msg_id)
                if "matches" in sample:
                    self.assertEqual(reply["content"]["matches"], sample["matches"])
    
    def test_is_complete(self):
        self.flush_channels()
        with self.subTest(status = "complete"):
            for sample in [
                'print complete code sample; echo "100% guarantee"',
                '123'
            ]:
                self.check_is_complete(sample, "complete")
        with self.subTest(status = "incomplete"):
            for sample in [
                "1()",
                "echo $((2 + 2)",
                # "something with open single quote '", # fixme: this fails. need to handle special chars
            ]:
                self.check_is_complete(sample, "incomplete")
