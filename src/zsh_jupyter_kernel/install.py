import argparse
import json
import os
import sys

from IPython.utils.tempdir import TemporaryDirectory
from jupyter_client.kernelspec import install_kernel_spec, get_kernel_spec, KernelSpec

def main(argv = None):
    try:
        args = parse_args(argv)

        if args.sys_prefix:
            args.prefix = sys.prefix
        if not args.prefix and not is_root():
            args.user = True

        with TemporaryDirectory() as tempd:
            os.chmod(tempd, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(tempd, 'kernel.json'), 'w') as f:
                json.dump(
                    {  # [kernel-specs]
                        "argv"          : [sys.executable, "-m", 'zsh_jupyter_kernel', "-f", "{connection_file}"],
                        "display_name"  : args.display_name,
                        "language"      : "zsh",
                        "interrupt_mode": "signal",
                    },
                    fp = f,
                    indent = 4,
                )
            try:
                install_kernel_spec(
                    source_dir = tempd,
                    kernel_name = args.name,
                    user = args.user,
                    prefix = args.prefix,
                )
            except OSError as e:
                print(e)
                print('you do not have appropriate permissions to install kernel in the specified location.\n'
                      'try installing in a location of your user using --user option'
                      ' or specify a custom value with --prefix.')
            else:
                spec: KernelSpec = get_kernel_spec(kernel_name = args.name)
                print(
                    f"installed z shell jupyter kernel spec in {spec.resource_dir}:\n"
                    f"""{json.dumps(dict(
                        argv = spec.argv,
                        env = spec.env,
                        display_name = spec.display_name,
                        language = spec.language,
                        interrupt_mode = spec.interrupt_mode,
                        metadata = spec.metadata,
                    ), indent = 4)}"""
                )
    except Exception as e:
        print(e)
        print('sorry, an unhandled error occured.'
              f' please report this bug to https://github.com/dan-oak/zsh-jupyter-kernel/issues')

def is_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms

def parse_args(argv) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--name',
        default = 'zsh',
        help = "directory name in the kernelspec repository. use this to specify a unique location for the kernel"
               " if you use more than one version, otherwise just skip it and use the default 'zsh' value."
               " kernelspec will be installed in {prefix}/{name}/share/jupyter/kernels/."
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
        help = "install to the given prefix. kernelspec will be installed in {prefix}/{name}/share/jupyter/kernels/",
    )
    return ap.parse_args(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
