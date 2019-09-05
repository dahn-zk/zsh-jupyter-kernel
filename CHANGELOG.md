# Changelog

## [3.1-3.2] - 2019-08-18 - 2019-09-05
### 🐞 Fixed
- Fixed issue when Zsh did not initialize if host used `add-zsh-hook` to
  customize prompts.
- Fixed issue when the kernel was timing out when a command did not 
  responded within 5 seconds.
- Fixed issue when the kernel was hanging on continuation prompt 
  (incomplete input).

## [3.0] - 2019-07-07
### ➕ Added
- 🔁 Now package is named `zsh-jupyter-kernel` for specificity
  and released at https://pypi.org/project/zsh-jupyter-kernel/

## [2.1-2.3] - 2019-06-30
### ➕ Added
- ⏹ Kernel interruption

## [2.0] - 2019-06-29
### ➕ Added
- 📝 Multiline support
- 🚀 This baby is on PyPi now: https://pypi.org/project/zsh-kernel/

## [1.0] - 2019-06-25
### Added
- Required basic kernel functionality for singe line Z shell commands.
