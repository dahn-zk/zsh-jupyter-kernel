import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import traceback
from tempfile import TemporaryDirectory
from typing import Literal

import jupyter_client.kernelspec

def main(argv = None):
    args = parse_args(argv)
    if args.prefix:
        install(args.name, args.display_name, custom_path_prefix = args.prefix)
    elif args.sys_prefix:
        install(args.name, args.display_name, path_prefix = 'sys')
    elif args.user:
        install(args.name, args.display_name, path_prefix = 'user')
    else:
        install(args.name, args.display_name)

def install(
        kernel_name: str = "zsh",
        display_name: str = "zsh",
        path_prefix: Literal['user', 'sys', 'default'] = 'default',
        custom_path_prefix: str = None,
):
    try:
        with TemporaryDirectory() as tempd:
            install_(kernel_name, display_name, path_prefix, custom_path_prefix, tempd)
    except Exception as e:
        traceback.print_exception(e)
        print()
        print("sorry, an unhandled error occured.")

def install_(kernel_name, display_name, path_prefix, custom_path_prefix, tempd):
    os.chmod(tempd, 0o755)  # starts off as 700, not user readable
    # [kernel-specs]
    with open(Path(tempd) / 'kernel.json', 'w') as f:
        d = {
            "argv": [sys.executable, "-m", 'zsh_jupyter_kernel', "-f", "{connection_file}"],
            "display_name": display_name,
            "language": "zsh",
            "interrupt_mode": "signal",
        }
        # noinspection PyTypeChecker
        json.dump(d, f, indent = 4)
    # logos
    for logof in ('logo-32x32.png', 'logo-64x64.png'):
        src = Path(__file__).with_name(logof)
        dst = Path(tempd) / logof
        shutil.copyfile(src, dst)
    #
    user = path_prefix == 'user'
    prefix = None
    if custom_path_prefix is not None:
        prefix = custom_path_prefix
    elif path_prefix == 'sys':
        prefix = sys.prefix
    try:
        jupyter_client.kernelspec.install_kernel_spec(
            source_dir = tempd,
            kernel_name = kernel_name,
            user = user and not (custom_path_prefix is not None),
            prefix = prefix,
        )
    except PermissionError as e:
        print(e)
        print('sorry, you do not have appropriate permissions to install kernel in the specified location.\n'
              'if you want to install in the default system-wide location, use elevated priviliges or login'
              'as an administrator.\n'
              'otherwise try installing in a current python environment location using --sys-prefix.\n'
              'use --help to read more.')
    else:
        spec = jupyter_client.kernelspec.get_kernel_spec(kernel_name = kernel_name)
        print(
            f"installed Z shell jupyter kernel spec in {spec.resource_dir}:\n"
            f"""{json.dumps(dict(
                argv = spec.argv,
                env = spec.env,
                display_name = spec.display_name,
                language = spec.language,
                interrupt_mode = spec.interrupt_mode,
                metadata = spec.metadata,
            ), indent = 4)}"""
        )

def install_logos(tempd):
    for logof in ('logo-32x32.png', 'logo-64x64.png'):
        src = Path(__file__).with_name(logof)
        dst = Path(tempd) / logof
        shutil.copyfile(src, dst)

def is_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms

class ArgumentFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter):
    pass

def parse_args(argv) -> argparse.Namespace:
    ksm = jupyter_client.kernelspec.KernelSpecManager()
    name = "${NAME}"
    # noinspection PyProtectedMember
    user_dir = ksm._get_destination_dir(name, user = True)
    # noinspection PyProtectedMember
    sys_dir = ksm._get_destination_dir(name, prefix = sys.prefix)
    # noinspection PyProtectedMember
    root_dir = ksm._get_destination_dir(name)
    ap = argparse.ArgumentParser(
        description = "install zsh jupyter kernel",
        epilog = f"the kernel will be installed in one of the locations:\n"
                 f"  by default: {root_dir}\n"
                 f"  using --sys-prefix: {sys_dir}\n"
                 f"  using --user: {user_dir}\n",
        formatter_class = ArgumentFormatter,
    )
    ap.add_argument(
        '--name',
        default = 'zsh',
        help = "directory name in the kernelspec repository. use this to specify a unique location for the kernel"
               " if you use more than one version, otherwise just skip it and use the default 'zsh' value."
               " since kernelspecs show up in urls and other places, a kernelspec is required to have a simple name,"
               " only containing ascii letters, ascii numbers, and the simple separators:"
               " - hyphen, . period, _ underscore.",
    )
    ap.add_argument(
        '--display-name',
        default = 'Z shell',
        help = "the kernel’s name as it should be displayed in the ui. unlike the --name used in the api,"
               " this can contain arbitrary unicode characters.",
    )
    ap.add_argument(
        '--user',
        action = 'store_true',
        help = "install to the per-user kernels registry. default if not root. ignored if --prefix is specified",
    )
    ap.add_argument(
        '--sys-prefix',
        action = 'store_true',
        help = "install to sys.prefix (e.g. a virtualenv, pipenv or conda env)",
    )
    ap.add_argument(
        '--prefix',
        help = "install to the given prefix.",
    )
    return ap.parse_args(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
