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
saved as {input-notebook-name}.{previous-kernelspec-name}.pynb
If CMD is 'check', target is optional and it reports any notebooks
with kernelspecs different to internal kernelspecs
(you can view the built-in kernelspecs with 'list' command)
as errors.

"""
import argparse
from pathlib import Path
from typing import Iterable, List
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
    },
    "azureml_310": {
        "name": "python310-sdkv2",
        "language": "python",
        "display_name": "Python 3.10 - SDK v2"
    },
    'papermill': {'display_name': 'papermill', 'language': 'python', 'name': 'papermill'},
    '.net-csharp':
   {'display_name': '.NET (C#)', 'language': 'C#', 'name': '.net-csharp'},
   '.net-powershell':
   {'display_name': '.NET (PowerShell)', 'language': 'PowerShell', 'name': '.net-powershell'},
}

_LEGAL_KERNELS = ["azureml_38", "papermill", ".net-csharp", ".net-powershell", "azureml_310"]


def check_notebooks(nb_path: str, k_tgts: Iterable[str], verbose: bool = False):
    """Check notebooks for valid kernelspec."""
    err_count = 0
    good_count = 0
    for nbook in _get_notebook_paths(nb_path):
        if ".ipynb_checkpoints" in str(nbook):
            continue
        try:
        	nb_obj = nbformat.read(str(nbook), as_version=4.0)
        except nbformat.reader.NotJSONError as err:
        	print(f"Error reading {nbook}\n{err}")
        	err_count += 1
        	continue
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
    print(f"{good_count} notebooks with no errors, {err_count} with errors")
    return good_count, err_count


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
            backup_path = (
                f"{str(nbook).strip(nbook.suffix)}-{current_kspec_name}{nbook.suffix}"
            )
            nbook.rename(backup_path)
            nbformat.write(nb_obj, str(nbook))
            continue
        if verbose:
            _print_nb_header(nbook)
            print(f"{kernelspec['name']} ok\n")
        good_count += 1
    print(f"{good_count} notebooks with no changes, {changed_count} updated")


def _add_script_args():
    parser = argparse.ArgumentParser(description="Notebook kernelspec checker.")
    parser.add_argument(
        "cmd", default="check", type=str, choices=["check", "list", "update"],
    )
    parser.add_argument(
        "--path", "-p", default=".", required=False, help="Path search for notebooks."
    )
    parser.add_argument(
        "--target", "-t", nargs="+", required=False, help="Target kernel spec(s) to check or set."
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

    krnl_tgts: List[str] = []
    if args.target:
        krnl_tgts = args.target
        for krnl_tgt in krnl_tgts:
            if krnl_tgt not in IP_KERNEL_SPEC:
                print("'target' must be a valid kernelspec definition")
                print("Valid kernel specs:")
                _view_targets()
                sys.exit(1)

    krnl_tgts = krnl_tgts or _LEGAL_KERNELS

    if not args.path:
        print("check and update commands need a 'path' parameter.")
        sys.exit(1)
    if args.cmd == "check":
        ok_count, err_count = check_notebooks(args.path, krnl_tgts, verbose=args.verbose)
        if err_count:
            sys.exit(1)
        sys.exit(0)

    if args.cmd == "update":
        if len(krnl_tgts) > 1:
            print(
                "Multiple targets specified for update.",
                f"Using first value {krnl_tgts[0]}"
            )
        krnl_tgt = krnl_tgts[0]
        if not krnl_tgt:
            print("A kernel target must be specified with 'update'.")
            sys.exit(1)
        set_kernelspec(args.path, krnl_tgt, verbose=args.verbose)
        sys.exit(0)
