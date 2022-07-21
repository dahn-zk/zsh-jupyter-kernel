import unittest
import pexpect

class Pexpect_ZSH_Test(unittest.TestCase):

    def test_echo(self):
        p = pexpect.spawn('zsh +o INTERACTIVE')
        p.logfile = io.BytesIO()
        p.sendline("echo 1")
        p.expect("1")  # timeouts if something is wrong
        self.assertEqual(p.logfile.getvalue(), b"echo 1\necho 1\r\n1\r\n")

if __name__ == '__main__':
    unittest.main()
