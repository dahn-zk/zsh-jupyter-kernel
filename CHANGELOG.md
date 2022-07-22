# changelog

## [3.4.1] - 2022-07-22
### removed
- removed logging for production build. this fixes failed installation when log files and directory cannot be created because of access permissions

## [3.4] - 2021-07-19
### fixed
- running `set` command which was previously stuck on execution.
- fixed an error when installing without specifying a `prefix`
- fixed a command to retrieve man pages

## [3.2] - 2019-09-05
### fixed
- fixed issue when zsh did not initialize if host used `add-zsh-hook` to
  customize prompts.
- fixed issue when the kernel was timing out when a command did not 
  responded within 5 seconds.
- fixed issue when the kernel was hanging on continuation prompt 
  (incomplete input).

## [3.0] - 2019-07-07
### changed
- now package is named `zsh-jupyter-kernel` for specificity
  and released at https://pypi.org/project/zsh-jupyter-kernel/

## [2.3] - 2019-06-30
### added
- ⏹ kernel interruption

## [2.0] - 2019-06-29
### added
- multiline support
- this baby is on pypi now: https://pypi.org/project/zsh-kernel/

## [1.0] - 2019-06-25
### added
- required basic kernel functionality for singe line z shell commands.
