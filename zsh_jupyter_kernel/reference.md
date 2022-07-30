## Reference
- pexpect-spawn: https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class
- pexpect-spawn-timeout: https://pexpect.readthedocs.io/en/stable/api/pexpect.html?highlight=timeout#spawn-class
- codecs: https://docs.python.org/3/library/codecs.html
- logging: https://docs.python-guide.org/writing/logging/
- zsh-options: https://linux.die.net/man/1/zshoptions
- zsh-functions: http://zsh.sourceforge.net/Doc/Release/Functions.html
- zsh-bracketed-paste: https://archive.zhimingwang.org/blog/2015-09-21-zsh-51-and-bracketed-paste.html
- zsh-hooks: http://zsh.sourceforge.net/Doc/Release/User-Contributions.html
  - Section "Manipulating Hook Functions"  
    Different plugins (e.g. oh-my-zsh with custom themes) use `precmd`/`preexec` hooks to set prompts. `add-zsh-hook -D <hook> <pattern>` allows to delete all assosiated functions from a hook.
- interrupt: https://jupyter-client.readthedocs.io/en/latest/messaging.html#kernel-interrupt
  Interrupt by message does not work now but works by signal. This is
confusing as hell to me as previously it was not working. Whatever...
- kernel-specs: https://jupyter-client.readthedocs.io/en/latest/kernels.html#kernelspecs
