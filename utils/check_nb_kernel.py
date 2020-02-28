import argparse
from pathlib import Path
import nbformat


PY36_KERNEL = {"name": ["python36", "python3"], "display_name": ["Python 3.6", "Python 3"], 'language': 'python'}


def check_notebooks(nb_path):
    notebooks = Path(nb_path).glob("**/*.ipynb")

    for nb_path in notebooks:
        if ".ipynb_checkpoints" in str(nb_path):
            continue
        nb = nbformat.read(str(nb_path), as_version=4.0)
        kernelspec = nb.get("metadata", {}).get("kernelspec", None)
        print(str(nb_path))
        print("-" * len(str(nb_path)))
        nb_ok = True
        for config in PY36_KERNEL:
            if not kernelspec:
                print("no kernel information.")
            if not kernelspec[config] in PY36_KERNEL[config]:
                print("Incorrect value in", config, end=". ")
                print(f"Should be: '{PY36_KERNEL[config]}'  Found:'{kernelspec[config]}'")
                nb_ok = False
        if nb_ok:
            print(f"{kernelspec['name']} ok"))
        else:
            print()

            
def _add_script_args():
    parser = argparse.ArgumentParser(description="Notebook kernelspec checker.")
    parser.add_argument(
        "--path", "-p", default=".", required=False, help="Path search for notebooks."
    )
    return parser


# pylint: disable=invalid-name
if __name__ == "__main__":
    arg_parser = _add_script_args()
    args = arg_parser.parse_args()

    check_notebooks(args.path)
    
