# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Checker for Python and msticpy versions."""
import importlib
import os
import re
import subprocess
import sys
from pkg_resources import parse_version
from IPython.display import display, HTML


MISSING_PKG_ERR = """
    <h3><font color='orange'>The package '<b>{package}</b>' is not
    installed or has an unsupported version (installed version = '{inst_ver}')</font></h3>
    <h4>Please install or upgrade this now</h4>
    Required version is {package}>={req_ver}
    """
MIN_PYTHON_VER_DEF = (3, 6)
MSTICPY_REQ_VERSION = (0, 9, 0)
VER_RGX = r"(?P<maj>\d+)\.(?P<min>\d+).(?P<pnt>\d+)(?P<suff>.*)"


def check_versions(
    min_py_ver=MIN_PYTHON_VER_DEF, min_mp_ver=MSTICPY_REQ_VERSION, extras=None, mp_release=None
):
    """
    Check the current versions of the Python kernel and MSTICPy.

    Parameters
    ----------
    min_py_ver : Union[Tuple[int, int], str]
        Minimum Python version
    min_mp_ver : Union[Tuple[int, int], str]
        Minimum MSTICPy version
    extras : Optional[List[str]]
        A list of extras required for MSTICPy
    mp_release : Optional[str]
        Override the MSTICPy release version. This
        can also be specified in the environment variable 'MP_TEST_VER'

    Raises
    ------
    RuntimeError
        If the Python version does not support the notebook.
        If the MSTICPy version does not support the notebook
        and the user chose not to upgrade

    """
    if isinstance(min_py_ver, str):
        min_py_ver = _get_pkg_version(min_py_ver).release
    check_python_ver(min_py_ver=min_py_ver)

    # Use the release ver specified in params, in the environment or
    # the notebook default.
    pkg_version = _get_pkg_version(min_mp_ver)
    mp_install_version = mp_release or os.environ.get("MP_TEST_VER", str(pkg_version))
    try:
        check_mp_ver(min_msticpy_ver=mp_install_version)
    except ImportError:
        sp_args = [
            "pip",
            "install",
            "--upgrade",
        ]
        mp_pkg_spec = f"msticpy[{','.join(extras)}]" if extras else "msticpy"
        mp_pkg_spec = f"{mp_pkg_spec}>={mp_install_version}"
        sp_args.append(mp_pkg_spec)
        subprocess.run(
            sp_args,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        # pylint: disable=unused-import, import-outside-toplevel
        if "msticpy" in sys.modules:
            importlib.reload(sys.modules["msticpy"])
        else:
            import msticpy
        # pylint: enable=unused-import, import-outside-toplevel
        check_mp_ver(min_mp_ver)
    except RuntimeError:
        print("Installation aborted.")

    _set_kql_env_vars(extras)


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
            "Python kernel version %s.%s.%s OK<br>"
            % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
        )
    )


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
    mp_min_pkg_ver = _get_pkg_version(min_msticpy_ver)

    display(HTML("Checking msticpy version..."))
    wrong_ver_err = "msticpy {mp_pkg_ver} or later is needed."
    inst_version = "none"
    try:
        import msticpy

        inst_version = _get_pkg_version(msticpy.__version__)
        if inst_version < mp_min_pkg_ver:
            raise ImportError(wrong_ver_err)

    except ImportError:
        display(
            HTML(
                MISSING_PKG_ERR.format(
                    package="msticpy",
                    inst_ver=inst_version,
                    req_ver=mp_min_pkg_ver,
                )
            )
        )
        resp = input("Install now? (y/n)")  # nosec
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
            """.format(pkg="msticpy", ver=mp_min_pkg_ver, curr_ver=inst_version)
            )
        )
        raise RuntimeError(wrong_ver_err)

    display(HTML("msticpy version %s.%s.%s OK<br>" % mp_version))


def _set_kql_env_vars(extras):
    jp_extended = ("azsentinel", "azuresentinel", "kql")
    # If running in
    if extras and any(extra for extra in extras if extra in jp_extended):
        os.environ["KQLMAGIC_EXTRAS_REQUIRES"] = "jupyter-extended"
    else:
        os.environ["KQLMAGIC_EXTRAS_REQUIRES"] = "jupyter-basic"


def _fmt_ver(version):
    return ".".join(str(ver) for ver in version)


def _fmt_dict_ver(version):
    return ".".join(str(ver) for ver in version.values)


def _get_pkg_version(version):
    if isinstance(version, str):
        return parse_version(version)
    elif isinstance(version, tuple):
        return parse_version(".".join(str(ver) for ver in version))
