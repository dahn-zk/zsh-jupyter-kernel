from queue import Empty
from unittest import SkipTest, TestCase, skip

from jupyter_client import KernelClient
from jupyter_client.manager import start_new_kernel, KernelManager
from jupyter_client.utils import run_sync

from .msgspec_v5 import validate_message

TIMEOUT = 1

class zsh_kernel_tests(TestCase):

    km : KernelManager
    kc : KernelClient

    @classmethod
    def setUpClass(cls):
        cls.km, cls.kc = start_new_kernel(kernel_name = "zsh")

    @classmethod
    def tearDownClass(cls):
        cls.kc.stop_channels()
        cls.km.shutdown_kernel()

    def setUp(self): print()

    def flush_channels(self):
        for channel in (self.kc.shell_channel, self.kc.iopub_channel):
            while True:
                try:
                    msg = run_sync(channel.get_msg)(timeout = 0.1)
                except Empty:
                    break
                else:
                    validate_message(msg)

    def execute(self, code : str, timeout = TIMEOUT, silent = False, store_history = True, stop_on_error = True):
        msg_id = self.kc.execute(code = code, silent = silent, store_history = store_history, stop_on_error = stop_on_error)

        reply = self.get_non_kernel_info_reply(timeout = timeout)
        validate_message(reply, "execute_reply", msg_id)

        busy_msg = run_sync(self.kc.iopub_channel.get_msg)(timeout = 1)
        validate_message(busy_msg, "status", msg_id)
        self.assertEqual(busy_msg["content"]["execution_state"], "busy")

        output_msgs = []
        while True:
            msg = run_sync(self.kc.iopub_channel.get_msg)(timeout = 0.1)
            validate_message(msg, msg["msg_type"], msg_id)
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
        validate_message(reply, "is_complete_reply", msg_id)
        if reply["content"]["status"] != status:
            msg = "for code sample\n  {!r}\nexpected {!r}, got {!r}."
            raise AssertionError(msg.format(sample, status, reply["content"]["status"]))

    def get_history(self, execute_first, timeout=TIMEOUT, **histargs):
        self.flush_channels()

        for code in execute_first:
            reply, output_msgs = self.execute(code)

        self.flush_channels()
        msg_id = self.kc.history(**histargs)

        reply = self.get_non_kernel_info_reply(timeout = timeout)
        validate_message(reply, "history_reply", msg_id)

        return reply

    def test_kernel_info(self):
        self.flush_channels()

        msg_id = self.kc.kernel_info()
        reply = self.kc.get_shell_msg(timeout = TIMEOUT)
        validate_message(reply, "kernel_info_reply", msg_id)

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

        reply, output_msgs = self.execute(code=">&2 print 'hello, world'")

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
                validate_message(reply, "complete_reply", msg_id)
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
                # "something with open single quote '", # this fails. need to handle special chars
            ]:
                self.check_is_complete(sample, "incomplete")

    @skip
    def test_execute_result(self):
        for sample in [
            {
                'code': 'print $((2 + 2))',
                'result': '4'
            },
            {
                'code': 'seq 10 | paste -sd+ | bc',
                'result': '55'
            },
        ]:
            with self.subTest(code = sample["code"]):
                self.flush_channels()

                reply, output_msgs = self.execute(sample["code"])

                self.assertEqual(reply["content"]["status"], "ok")

                self.assertGreaterEqual(len(output_msgs), 1)

                found = False
                for msg in output_msgs:
                    if msg["msg_type"] == "execute_result":
                        found = True
                    else:
                        continue
                    mime = sample.get("mime", "text/plain")
                    self.assertIn(mime, msg["content"]["data"])
                    if "result" in sample:
                        self.assertEqual(msg["content"]["data"][mime], sample["result"])
                assert found, "execute_result message not found"

    @skip
    def test_display_data(self):
        for sample in []:
            with self.subTest(code=sample["code"]):
                self.flush_channels()
                reply, output_msgs = self.execute(sample["code"])

                self.assertEqual(reply["content"]["status"], "ok")

                self.assertGreaterEqual(len(output_msgs), 1)
                found = False
                for msg in output_msgs:
                    if msg["msg_type"] == "display_data":
                        found = True
                    else:
                        continue
                    self.assertIn(sample["mime"], msg["content"]["data"])
                assert found, "display_data message not found"

    @skip
    def test_history(self):
        codes = [s["code"] for s in self.code_execute_result]
        _ = [s.get("result", "") for s in self.code_execute_result]
        n = len(codes)

        session = start = None

        with self.subTest(hist_access_type="tail"):
            if "tail" not in self.supported_history_operations:
                raise SkipTest
            reply = self.get_history(codes, output=False, raw=True, hist_access_type="tail", n=n)
            self.assertEqual(len(reply["content"]["history"]), n)
            self.assertEqual(len(reply["content"]["history"][0]), 3)
            self.assertEqual(codes, [h[2] for h in reply["content"]["history"]])

            session, start = reply["content"]["history"][0][0:2]
            with self.subTest(output=True):
                reply = self.get_history(
                    codes, output=True, raw=True, hist_access_type="tail", n=n
                )
                self.assertEqual(len(reply["content"]["history"][0][2]), 2)

        with self.subTest(hist_access_type="range"):
            if "range" not in self.supported_history_operations:
                raise SkipTest
            if session is None:
                raise SkipTest
            reply = self.get_history(
                codes,
                output=False,
                raw=True,
                hist_access_type="range",
                session=session,
                start=start,
                stop=start + 1,
            )
            self.assertEqual(len(reply["content"]["history"]), 1)
            self.assertEqual(reply["content"]["history"][0][0], session)
            self.assertEqual(reply["content"]["history"][0][1], start)

        with self.subTest(hist_access_type="search"):
            if not self.code_history_pattern:
                raise SkipTest
            if "search" not in self.supported_history_operations:
                raise SkipTest

            with self.subTest(subsearch="normal"):
                reply = self.get_history(
                    codes,
                    output=False,
                    raw=True,
                    hist_access_type="search",
                    pattern=self.code_history_pattern,
                )
                self.assertGreaterEqual(len(reply["content"]["history"]), 1)
            with self.subTest(subsearch="unique"):
                reply = self.get_history(
                    codes,
                    output=False,
                    raw=True,
                    hist_access_type="search",
                    pattern=self.code_history_pattern,
                    unique=True,
                )
                self.assertEqual(len(reply["content"]["history"]), 1)
            with self.subTest(subsearch="n"):
                reply = self.get_history(
                    codes,
                    output=False,
                    raw=True,
                    hist_access_type="search",
                    pattern=self.code_history_pattern,
                    n=3,
                )
                self.assertEqual(len(reply["content"]["history"]), 3)

    @skip
    def test_inspect(self):
        self.flush_channels()
        msg_id = self.kc.inspect(self.code_inspect_sample)
        reply = self.get_non_kernel_info_reply(timeout=TIMEOUT)
        validate_message(reply, "inspect_reply", msg_id)

        self.assertEqual(reply["content"]["status"], "ok")
        self.assertTrue(reply["content"]["found"])
        self.assertGreaterEqual(len(reply["content"]["data"]), 1)

    @skip
    def test_clear_output(self):
        if not self.code_clear_output:
            raise SkipTest

        self.flush_channels()
        reply, output_msgs = self.execute(code=self.code_clear_output)
        self.assertEqual(reply["content"]["status"], "ok")
        self.assertGreaterEqual(len(output_msgs), 1)

        found = False
        for msg in output_msgs:
            if msg["msg_type"] == "clear_output":
                found = True
            else:
                continue
        assert found, "clear_output message not found"
