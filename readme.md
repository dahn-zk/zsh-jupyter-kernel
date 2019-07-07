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

### 🔮
Everything else under active development. Create an [Issue][issue] to request
a feature.
<p align=center>
<a href=roadmap.md>Roadmap ✅</a>
•
<a href=contributing.md>Contribution 👍</a>
•
<a href=license.txt>License 🤝</a>
</p>

## Install

### Pipenv
[`install.sh`](misc/install.sh)
```sh
pipenv --python 3.7 install zsh-kernel jupyter-notebook
pipenv run python -m zsh_jupyter_kernel.install --sys-prefix
```

### Pip
```sh
python -m pip install zsh-kernel
python -m zsh_jupyter_kernel.install
```

## Run
[`lab.sh`](misc/lab.sh)
```sh
pipenv run jupyter notebook
```

## Thanks to
- https://github.com/Valodim/zsh-capture-completion for script to get Zsh completions as data
- Jupyter Development Team for Jupyter itself

[issue]: https://github.com/danylo-dubinin/zsh-jupyter-kernel/issues/new
