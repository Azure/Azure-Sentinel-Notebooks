# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Checker/Updater for Notebook kernelspec versions.

check_nb_kernel.py CMD [-h] [--path PATH] [--target TARGET] [--verbose]

CMD is one of:
  {check, list, update} (default is "check")

  list - shows list of internal kernelspecs that can be used
  check - checks the notebook or notebooks for comformance to kernspecs
  update - updates notebook or notebooks to target kernelspec

optional arguments:
  -h, --help            show this help message and exit
  --path PATH, -p PATH  Path search for notebooks. Can be a single file,
                        a directory path or a 'glob'-compatible wildcard.
                        (e.g. "*" for all files in current folder, "**/*"
                        for all files in folder and subfolders)
                        Defaults to current directory.
  --target TARGET, -t TARGET
                        Target kernel spec to check or set.
                        Required for 'update' command
  --verbose, -v         Show details of all checked notebooks. Otherwise
                        only list notebooks with errors or updated notebooks.

Notes
-----

If CMD is 'update' you must specify a kernelspec target. The updated
notebook is written to the same name as the input. The old version is
saved as {input-notebook-name}.{previous-kernelspec-name}
If CMD is 'view', target is optional and it reports any notebooks
with kernelspecs different to internal kernelspecs (view with 'list' command)
as errors.

"""
import argparse
from pathlib import Path
from typing import Optional, Iterable
import sys

import nbformat


IP_KERNEL_SPEC = {
    "python36": {
        "name": "python36",
        "language": "python",
        "display_name": "Python 3.6",
    },
    "python3": {"name": "python3", "language": "python", "display_name": "Python 3"},
    "azureml_36": {
        "name": "python3-azureml",
        "language": "python",
        "display_name": "Python 3.6 - AzureML"
    },
    "azureml_38": {
        "name": "python38-azureml",
        "language": "python",
        "display_name": "Python 3.8 - AzureML"
    }
}


def check_notebooks(nb_path: str, k_tgts: Iterable[str], verbose: bool = False):
    """Check notebooks for valid kernelspec."""
    err_count = 0
    good_count = 0
    for nbook in _get_notebook_paths(nb_path):
        if ".ipynb_checkpoints" in str(nbook):
            continue
        nb_obj = nbformat.read(str(nbook), as_version=4.0)
        kernelspec = nb_obj.get("metadata", {}).get("kernelspec", None)
        if not kernelspec:
            print("Error: no kernel information.")
            continue
        nb_ok = False
        for config in k_tgts:
            tgt_spec = IP_KERNEL_SPEC[config]
            for k_name, k_item in kernelspec.items():
                if tgt_spec[k_name] != k_item:
                    break
            else:
                nb_ok = True
        if not nb_ok:
            err_count += 1
            _print_nb_header(nbook)
            print("ERROR - Invalid kernelspec '" f"{kernelspec.get('name')}" "'")
            print("  ", kernelspec, "\n")
            continue
        if verbose:
            _print_nb_header(nbook)
            print(f"{kernelspec['name']} ok\n")
        good_count += 1
    print(f"{good_count} with no errors, {err_count} with errors")


def _get_notebook_paths(nb_path: str):
    """Generate notebook paths."""
    if "*" in nb_path:
        for glob_path in Path().glob(nb_path):
            if glob_path.is_file() and glob_path.suffix.casefold() == ".ipynb":
                yield glob_path
    elif Path(nb_path).is_dir():
        yield from Path(nb_path).glob("*.ipynb")
    elif Path(nb_path).is_file():
        yield Path(nb_path)


def _print_nb_header(nbook_path):
    print(str(nbook_path.name))
    print("-" * len(str(nbook_path.name)))
    print(str(nbook_path.resolve()))


def set_kernelspec(nb_path: str, k_tgt: str, verbose: bool = False):
    """Update specified notebooks to `k_tgt` kernelspec."""
    changed_count = 0
    good_count = 0
    for nbook in _get_notebook_paths(nb_path):
        if ".ipynb_checkpoints" in str(nbook):
            continue
        with open(str(nbook), "r") as nb_read:
            nb_obj = nbformat.read(nb_read, as_version=4.0)
        kernelspec = nb_obj.get("metadata", {}).get("kernelspec", None)
        current_kspec_name = kernelspec.get("name")
        if not kernelspec:
            print("Error: no kernel information.")
            continue
        updated = False
        tgt_spec = IP_KERNEL_SPEC[k_tgt]
        for k_name, k_item in kernelspec.items():
            if tgt_spec[k_name] != k_item:
                updated = True
                kernelspec[k_name] = tgt_spec[k_name]
        if updated:
            changed_count += 1
            _print_nb_header(nbook)
            print(
                f"Kernelspec updated from '{current_kspec_name}' to '"
                f"{kernelspec.get('name')}"
                "'"
            )
            print("  ", kernelspec, "\n")
            nbook.rename(f"{str(nbook)}.{current_kspec_name}")
            nbformat.write(nb_obj, str(nbook))
            continue
        if verbose:
            _print_nb_header(nbook)
            print(f"{kernelspec['name']} ok\n")
        good_count += 1
    print(f"{good_count} with no changes, {changed_count} updated")


def _add_script_args():
    parser = argparse.ArgumentParser(description="Notebook kernelspec checker.")
    parser.add_argument(
        "cmd", default="check", type=str, choices=["check", "list", "update"],
    )
    parser.add_argument(
        "--path", "-p", default=".", required=False, help="Path search for notebooks."
    )
    parser.add_argument(
        "--target", "-t", required=False, help="Target kernel spec to check or set."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show details of all checked notebooks.",
    )
    return parser


def _view_targets():
    print("Valid targets:")
    for kernel, settings in IP_KERNEL_SPEC.items():
        print(f"{kernel}:")
        print("  ", settings)


# pylint: disable=invalid-name
if __name__ == "__main__":
    arg_parser = _add_script_args()
    args = arg_parser.parse_args()

    if args.cmd == "list":
        _view_targets()
        sys.exit(0)

    krnl_tgt: Optional[str] = None
    if args.target:
        krnl_tgt = args.target
        if krnl_tgt not in IP_KERNEL_SPEC:
            print("'target' must be a valid kernelspec definition")
            print("Valid kernel specs:")
            _view_targets()
            sys.exit(1)

    if krnl_tgt is not None:
        krnl_tgts = [krnl_tgt]
    else:
        krnl_tgts = list(IP_KERNEL_SPEC.keys())

    if not args.path:
        print("check and update commands need a 'path' parameter.")
        sys.exit(1)
    if args.cmd == "check":
        check_notebooks(args.path, krnl_tgts, verbose=args.verbose)
        sys.exit(0)

    if args.cmd == "update":
        if not krnl_tgt:
            print("A kernel target must be specified with 'update'.")
            sys.exit(1)
        set_kernelspec(args.path, krnl_tgt, verbose=args.verbose)
        sys.exit(0)
