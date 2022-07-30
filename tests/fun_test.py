from unittest import TestCase, main

from zsh_jupyter_kernel.fun import find_word_at_pos

class fun_test(TestCase):

    def test_get_word_at_pos(self):
        text = "non! autem~42? [ut]"
        t = [
            "non", "non", "non", "non",
            "",
            "autem", "autem", "autem", "autem", "autem", "autem",
            "42?", "42?", "42?", "42?"
            "", "",
            "ut", "ut",
        ]
        for i, a in enumerate(t):
            self.assertEqual(a, find_word_at_pos(text, pos = i), f"pos = {i}")


if __name__ == '__main__':
    main()
