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

### 🔮
Other features are under active development.  
<p align=center>
<a href=roadmap.md>Roadmap ✅</a>
•
<a href=CONTRIBUTING.md>Contribution 👍</a>
•
<a href=LICENSE>License 🤝</a>
</p>

## Install

### Pipenv
[`install.sh`](misc/install.sh)
```sh
pipenv --python 3.7 install zsh-kernel jupyter-notebook
pipenv run python -m zsh_kernel.install --sys-prefix
```

### Pip
```sh
python -m pip install zsh-kernel
python -m zsh_kernel.install
```

## Run
[`lab.sh`](misc/lab.sh)
```sh
pipenv run jupyter notebook
```
