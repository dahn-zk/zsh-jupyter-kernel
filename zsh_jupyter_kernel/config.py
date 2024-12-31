__all__ = ['config']

import os
from pathlib import Path
from typing import Any

config: dict[str, Any] = {}

path = Path(__file__)

version = path.with_name('version.txt').read_text()

logging_enabled = os.environ.get("ZSH_JUPYTER_KERNEL_LOGGING_ENABLED", "0") == "1"
config["logging_enabled"] = logging_enabled
logging_level = os.environ.get("ZSH_JUPYTER_KERNEL_LOGGING_LEVEL", "INFO")
config["logging_level"] = logging_level
logging_dir_path = Path(os.environ.get("ZSH_JUPYTER_KERNEL_LOGGING_PATH", path.parent / "../logs"))
config["logging_dir_path"] = str(logging_dir_path)
if logging_enabled:
    logging_dir_path.mkdir(parents = True, exist_ok = True)
    logging_file_path = logging_dir_path / "kernel.log"
    config["logging_file_path"] = str(logging_file_path)
    config["logging_formatter"] = "%(asctime)s | %(name)-10s | %(levelname)-6s | %(message)s"

config["pexpect"] = {
    "encoding": "utf-8",
    "codec_errors": "replace",  # [codecs]
    "timeout": None,  # [pexpect-spawn-timeout]
    "logging_file_path": str(logging_dir_path / "pexpect.log"),
}

config["zsh"] = {
    "init_cmds": [
        "autoload -Uz add-zsh-hook",
        "add-zsh-hook -D precmd \*",
        "add-zsh-hook -D preexec \*",
        # [zsh-hooks]
        "precmd() {}",
        "preexec() {}",
        # [zsh-functions]
    ],
    "config_cmds": [
        "unset zle_bracketed_paste",  # [zsh-bracketed-paste]
        "zle_highlight=(none)",  # https://linux.die.net/man/1/zshzle
    ],
}

config["kernel"] = {
    "code_completion": {"cmd": str(path.with_name("capture.zsh")) + " {}"},
    "info": {
        "protocol_version": "5.3",
        "implementation": "ZshKernel",
        "implementation_version": version,
        "language_info": {
            "name": "zsh",
            "version": "5.7.1",
            "mimetype": "text/x-zsh",
            "file_extension": ".zsh",
            "pygments_lexer": "shell",
            "codemirror_mode": "shell",
        },
        "banner": path.with_name("banner.txt").read_text(),
    },
}

if __name__ == "__main__":
    import json
    print(json.dumps(config, indent = 4))
