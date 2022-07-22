# zsh kernel for jupyter

a simple z shell jupyter kernel powered by pexpect and enthusiasm

support link: https://ko-fi.com/danoak

![screenshot](misc/example.png)


## installation

### pipenv
```sh
pipenv --python 3.10 install notebook zsh_jupyter_kernel
pipenv run python -m zsh_jupyter_kernel.install --sys-prefix
```

### pip
```sh
python3 -m pip install notebook zsh_jupyter_kernel
python3 -m zsh_jupyter_kernel.install --sys-prefix
```


## technical overview

### how does code execution work  
the kernel configures zsh prompt string to its own custom value.  
when a user requests a cell execution, the code is sent to the kernel.   
then the kernel puts the frontend on hold, sends the code to zsh process, and waits for the prompt string to release the frontend and let the user request more code execution.

### code completion
code completion is powered by quite a non-trivial script that involves multiple steps, including spawning another temporary zsh process and capturing completion options into a data structure that jupyter frontend understands.

### code inspection
code inspection is done by `man --pager ul` which sends the whole man page to the frontend.

### code completeness
code completeness is checked with the temporary zsh process and help of `EXEC` zsh option, which allows switching off code execution and simply check if the code is complete using the exit code of the zsh process itself.

### stderr 
stderr content is just sent to the front-end as regular stdout.

### stdin
stdin is not supported because of the execution system when a process spawned by a user waits for stdin, there is no way to detect it.

### missing features
- history
- rich html output for things like images and tables
- stdin. might be possible with or without the current system 
- pagers. might be possible or not
- stored and referenceable outputs
 