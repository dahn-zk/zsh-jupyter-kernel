# Zsh kernel for Jupyter

![](https://raw.githubusercontent.com/dahn-zk/zsh-jupyter-kernel/master/screenshots/example.png)

a simple Z Shell Jupyter kernel powered by Python, IPyKernel, Pexpect,
and enthusiasm — turn your scripts into notebooks!

## technical details

the kernel launches Zsh as if it was a regular process launched from your
terminal with a few minor settings to make sure it works with Jupyter. there is
slight chance it wont work with super complicated zshrc setups, but it works
with majority of configs including oh-my-zsh.

### code execution
          
the kernel configures Zsh prompt string to its own custom value.
when a user requests a cell execution, the code is sent to the kernel.
then the kernel puts the frontend on hold, sends the code to Zsh process, and
waits for the prompt string to release the frontend and let the user request
more code execution.

### code completion
                        
![](https://raw.githubusercontent.com/dahn-zk/zsh-jupyter-kernel/master/screenshots/completion.png)

code completion is powered by quite a non-trivial script that involves multiple
steps, including spawning another temporary Zsh process and capturing completion
options into a data structure that jupyter frontend understands.

### code inspection
                  
![](https://raw.githubusercontent.com/dahn-zk/zsh-jupyter-kernel/master/screenshots/inspection.png)

code inspection is done by `man --pager ul` which sends the whole man page to
the frontend.

### code completeness

code completeness is checked with the temporary Zsh process and help of `EXEC`
Zsh option, which allows switching off code execution and simply check if the
code is complete using the exit code of the Zsh process itself.

### stderr

stderr content is just sent to the front-end as regular stdout the same way it
is in a terminal.

### stdin

stdin is not supported because of the execution system when a process spawned by
a user waits for stdin, there is no way to detect it.

jupyter is a request-reply system, and Zsh as a shell that constantly receives
input and prints whatever current processes want to output. there is no clear
start and end of a code execution in a shell unlike in jupyter system: a
front-end sends a code from a cell to a kernel and waits until the kernel sends
the full output back.

because of these two different ways of interacting with user Zsh jupyter kernel
cannot process stdin in a way python kernel does on `input()`, meaning you will
not be able to enter a sudo password or answer y/n to prompts or use a pager
like less. when a spawned program waits for a user input, you will need to
interrupt the kernel and use any options which do not require input.
