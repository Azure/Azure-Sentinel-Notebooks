# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Checker for Python and msticpy versions."""
import os
import re
import subprocess
import sys
from IPython.display import display, HTML


MISSING_PKG_ERR = """
    <h3><font color='orange'>The package '<b>{package}</b>' is not
    installed or has an unsupported version {inst_ver}</font></h3>
    <h4>Please install or upgrade this now</h4>
    Required version is {package}>={req_ver}
    """
MIN_PYTHON_VER_DEF = (3, 6)
MSTICPY_REQ_VERSION = (0, 9, 0)
VER_RGX = r"(?P<maj>\d+)\.(?P<min>\d+).(?P<pnt>\d+)(?P<suff>.*)"


def check_versions(
    min_py_ver=MIN_PYTHON_VER_DEF, min_mp_ver=MSTICPY_REQ_VERSION, extras=None
):
    """
    Check the current versions of the Python kernel and MSTICPy.

    Parameters
    ----------
    min_py_ver : Tuple[int, int]
        Minimum Python version
    min_py_ver : Tuple[int, int]
        Minimum MSTICPy version

    Raises
    ------
    RuntimeError
        If the Python version does not support the notebook.
        If the MSTICPy version does not support the notebook
        and the user chose not to upgrade

    """
    check_python_ver(min_py_ver=min_py_ver)
    try:
        check_mp_ver(min_msticpy_ver=min_mp_ver)
    except ImportError:
        sp_args = [
            "pip",
            "install",
            "--upgrade",
        ]
        if extras:
            sp_args.append(f"msticpy[{', '.join(extras)}]")
        else:
            sp_args.append("msticpy")
        subprocess.run(
            sp_args,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        if "msticpy" in sys.modules:
            importlib.reload(sys.modules["msticpy"])
        else:
            import msticpy
        check_mp_ver(REQ_MSTICPY_VER)


def check_python_ver(min_py_ver=MIN_PYTHON_VER_DEF):
    """
    Check the current version of the Python kernel.

    Parameters
    ----------
    min_py_ver : Tuple[int, int]
        Minimum Python version

    Raises
    ------
    RuntimeError
        If the Python version does not support the notebook.

    """
    display(HTML("Checking Python kernel version..."))
    if sys.version_info < min_py_ver:
        display(
            HTML(
                """
            <h3><font color='red'>This notebook requires a later notebook
            (Python) kernel version.</h3></font>
            From the Notebook menu (above), choose <b>Kernel</b> then
            <b>Change Kernel...</b> from the menu.<br>
            Select a <b>Python %s.%s</b> (or later) version kernel and then re-run
            this cell.<br><br>
            """
                % min_py_ver
            )
        )
        display(
            HTML(
                """
            Please see the <b><a href="./TroubleShootingNotebooks.ipynb">
            TroubleShootingNotebooks</a></b>
            in this folder for more information<br><br><hr>
            """
            )
        )
        raise RuntimeError("Python %s.%s or later kernel is required." % min_py_ver)

    display(
        HTML(
            "Python kernel version %s.%s.%s OK"
            % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
        )
    )

    os.environ["KQLMAGIC_EXTRAS_REQUIRES"] = "jupyter-extended"


# pylint: disable=import-outside-toplevel
def check_mp_ver(min_msticpy_ver=MSTICPY_REQ_VERSION):
    """
    Check and optionally update the current version of msticpy.

    Parameters
    ----------
    min_py_ver : Tuple[int, int]
        Minimum MSTICPy version

    Raises
    ------
    RuntimeError
        If the MSTICPy version does not support the notebook
        and the user chose not to upgrade.

    ImportError
        If MSTICPy version is insufficient and we need to upgrade

    """
    display(HTML("Checking msticpy version..."))
    wrong_ver_err = "msticpy %s.%s.%s or later is needed." % min_msticpy_ver
    curr_ver_text = "none"
    try:
        import msticpy

        curr_ver_text = msticpy.__version__
        mp_version = _get_version(msticpy)
        if mp_version < min_msticpy_ver:
            raise ImportError(wrong_ver_err)

    except ImportError:
        display(
            HTML(
                MISSING_PKG_ERR.format(
                    package="msticpy",
                    inst_ver=curr_ver_text,
                    req_ver=_fmt_ver(min_msticpy_ver),
                )
            )
        )
        resp = input("Install? (y/n)")  # nosec
        if resp.casefold().startswith("y"):
            raise

        display(
            HTML(
                """
            <h3><font color='red'>The notebook cannot be run without
            the correct version of '<b>{pkg}</b>' ({ver} or later).
            </font></h3>
            Currently installed version is {curr_ver}
            Please see the <b><a href="./TroubleShootingNotebooks.ipynb">
            TroubleShootingNotebooks</a></b>
            in this folder for more information<br><br><hr>
            """.format(pkg="msticpy", ver=_fmt_ver(min_msticpy_ver), curr_ver=curr_ver_text)
            )
        )
        raise RuntimeError(wrong_ver_err)

    display(HTML("msticpy version %s.%s.%s OK" % mp_version))


def _fmt_ver(version):
    return ".".join(str(ver) for ver in version)

def _get_version(module):
    ver_match = re.match(VER_RGX, module.__version__)
    if ver_match:
        ver_dict = ver_match.groupdict()
        return int(ver_dict["maj"]), int(ver_dict["min"]), int(ver_dict["pnt"])
    return (0, 0, 0)