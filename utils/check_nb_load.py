# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Check that notebooks can be loaded by nbconvert."""

from pathlib import Path
from nbconvert import HTMLExporter
import nbformat


__author__ = "Ian Hellen"

for nb_file in Path(".").rglob("*.ipynb"):
    if ".ipynb_checkpoints" in str(nb_file):
        continue
    print(f"Checking {nb_file}: ", end="")
    try:
        nb_node = nbformat.read(str(nb_file), as_version=nbformat.NO_CONVERT)

        html_exporter = HTMLExporter(template_name='classic')
        (body, resources) = html_exporter.from_notebook_node(nb_node)
        print("ok")
    except Exception as err:
        print(f"\nERROR loading notebook {nb_file}")
        print(err)
        print(err.args)

