# Z shell kernel for Jupyter

## Features

### ▶️ Execute
Execute any multiline Zsh code which does not wait for `stdin`.
A pseudo terminal process runs until a kernel is stopped and is common
for all notebook cells.

![Execution screenshot](misc/example.png)

### ⏹ Interrupt
Interrupt any code as in any terminal.

### 🔎 Inspect
Get `man` pages for commands under cursor.

![Inspection screenshot](misc/inspection.png)

### 🧰 Complete
Complete code using all completions as in terminal.

![Completion screenshot](misc/completion.png)

### 😎 Just do it
See more supported features in [Misc](misc/).

### ⚠️ Limitations
- Currently not possible to run commands which wait for input.
- Due to multiple links in data transfering (zsh <> pexpect <> python <> zeromq <> browser) the application is significantly slower than plain zsh.

### 🔮
Everything else under active development. Create an [Issue][issue] to request
a feature.
<p align=center>
<a href=roadmap.md>Roadmap ✅</a>
•
<a href=CONTRIBUTING.md>Contribution 👍</a>
•
<a href=LICENSE.txt>License 🤝</a>
</p>

## Install

### Pipenv
```sh
pipenv --python 3.7 install notebook zsh_jupyter_kernel
pipenv run python -m zsh_jupyter_kernel.install --sys-prefix
```

### Pip
```sh
python3 -m pip install notebook zsh_jupyter_kernel
python3 -m zsh_jupyter_kernel.install --sys-prefix
```

## Run

### Dockerized
[`./docker.zsh`](./docker.zsh)
```sh
docker build --tag zsh-jupyter-kernel:3.2 .
docker run --rm --interactive --tty \
  --publish=8889:8888 \
  --volume=$PWD/test:/home/jovyan \
  --name=zsh-jupyter-kernel \
  zsh-jupyter-kernel:3.2
```

### Native
[`lab.sh`](misc/lab.sh)
```sh
pipenv run jupyter notebook
```

## Thanks to
- https://github.com/Valodim/zsh-capture-completion for script to get Zsh completions as data
- https://github.com/eiro/play-jupyter for initial Dockerfile and doc fixes
- Jupyter Development Team for Jupyter itself

[issue]: https://github.com/danylo-dubinin/zsh-jupyter-kernel/issues/new
