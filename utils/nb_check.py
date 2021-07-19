# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Checker for Python and msticpy versions."""
import importlib
import json
import os
import re
import socket
import sys
import urllib
from pathlib import Path
from urllib import request

from IPython import get_ipython
from IPython.display import HTML, display
from pkg_resources import parse_version

__version__ = "2.0.0"

AZ_GET_STARTED = (
    "https://github.com/Azure/Azure-Sentinel-Notebooks/blob/master/A%20Getting"
    "%20Started%20Guide%20For%20Azure%20Sentinel%20ML%20Notebooks.ipynb"
)
TROUBLE_SHOOTING = (
    "https://github.com/Azure/Azure-Sentinel-Notebooks/blob/master/"
    "TroubleShootingNotebooks.ipynb"
)
MISSING_PKG_ERR = """
    <h4><font color='orange'>The package '<b>{package}</b>' is not
    installed or has an unsupported version (installed version = '{inst_ver}')</font></h4>
    Please install or upgrade before continuing: required version is {package}>={req_ver}
    """
MP_INSTALL_FAILED = """
    <h4><font color='red'>The notebook may not run correctly without
    the correct version of '<b>{pkg}</b>' ({ver} or later).</font></h4>
    Please see the <a href="{nbk_uri}">
    Getting Started Guide For Azure Sentinel ML Notebooks</a></b>
    for more information<br><hr>
"""
RELOAD_MP = """
    <h4><font color='orange'>Kernel restart needed</h4>
    An error was detected trying to load the updated version of MSTICPy.<br>
    Please restart the notebook kernel and re-run this cell - it should
    run without error.
    """

MIN_PYTHON_VER_DEF = (3, 6)
MSTICPY_REQ_VERSION = (0, 9, 0)
VER_RGX = r"(?P<maj>\d+)\.(?P<min>\d+).(?P<pnt>\d+)(?P<suff>.*)"
MP_ENV_VAR = "MSTICPYCONFIG"
MP_FILE = "msticpyconfig.yaml"
NB_CHECK_URI = (
    "https://raw.githubusercontent.com/Azure/Azure-Sentinel-"
    "Notebooks/master/utils/nb_check.py"
)

_IN_AML = os.environ.get("APPSETTING_WEBSITE_SITE_NAME") == "AMLComputeInstance"


def check_versions(
    min_py_ver=MIN_PYTHON_VER_DEF,
    min_mp_ver=MSTICPY_REQ_VERSION,
    extras=None,
    mp_release=None,
    pip_quiet=True,
    **kwargs,
):
    """
    Check the current versions of the Python kernel and MSTICPy.

    Parameters
    ----------
    min_py_ver : Union[Tuple[int, int], str]
        Minimum Python version
    min_mp_ver : Union[Tuple[int, int], str]
        Minimum MSTICPy version
    extras : Optional[List[str]], optional
        A list of extras required for MSTICPy
    mp_release : Optional[str], optional
        Override the MSTICPy release version. This
        can also be specified in the environment variable 'MP_TEST_VER'
    pip_quiet : bool, optional
        If True (default) will suppress all output from pip except
        warnings and errors. False will display normal output.

    Raises
    ------
    RuntimeError
        If the Python version does not support the notebook.
        If the MSTICPy version does not support the notebook
        and the user chose not to upgrade

    """
    del kwargs
    _disp_html("Note: you may need to scroll down this cell to see the full output.")
    _disp_html("<h4>Starting notebook pre-checks...</h4>")
    if isinstance(min_py_ver, str):
        min_py_ver = _get_pkg_version(min_py_ver).release
    check_python_ver(min_py_ver=min_py_ver)

    _check_mp_install(min_mp_ver, mp_release, extras, pip_quiet)
    _disp_html("<h4>Notebook pre-checks complete.</h4>")


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
    _disp_html("Checking Python kernel version...")
    if sys.version_info < min_py_ver:
        _disp_html(
            """
            <h4><font color='red'>This notebook requires a later notebook
            (Python) kernel version.</h4></font>
            Select a kernel from the notebook toolbar (above), that is Python
            3.6 or later (Python 3.8 recommended)<br>
            """
            % min_py_ver
        )
        _disp_html(
            f"""
            Please see the <a href="{TROUBLE_SHOOTING}">TroubleShootingNotebooks</a>
            for more information<br><br><hr>
            """
        )
        raise RuntimeError("Python %s.%s or later kernel is required." % min_py_ver)

    if sys.version_info < (3, 8, 0):
        _disp_html(
            "Recommended: switch to using the 'Python 3.8 - AzureML' notebook kernel"
            " if this is available."
        )
    _disp_html(
        "Info: Python kernel version %s.%s.%s OK<br>"
        % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
    )


def _check_mp_install(min_mp_ver, mp_release, extras, pip_quiet):
    """Check for and try to install required MSTICPy version."""
    # Use the release ver specified in params, in the environment or
    # the notebook default.
    pkg_version = _get_pkg_version(min_mp_ver)
    mp_install_version = mp_release or os.environ.get("MP_TEST_VER", str(pkg_version))
    exact_version = bool(mp_release or os.environ.get("MP_TEST_VER"))

    try:
        check_mp_ver(min_msticpy_ver=mp_install_version)
        if extras:
            # If any extras are specified, always trigger an install
            _disp_html("Running install to ensure extras are installed...<br>")
            _install_mp(
                mp_install_version=mp_install_version,
                exact_version=exact_version,
                extras=extras,
                quiet=pip_quiet,
            )
    except ImportError:
        _install_mp(
            mp_install_version=mp_install_version,
            exact_version=exact_version,
            extras=extras,
            quiet=pip_quiet,
        )
        _disp_html("Installation completed. Attempting to re-import/reload MSTICPy...")
        # pylint: disable=unused-import, import-outside-toplevel
        if "msticpy" in sys.modules:
            try:
                importlib.reload(sys.modules["msticpy"])
            except ImportError:
                _disp_html(RELOAD_MP)
        else:
            import msticpy
        # pylint: enable=unused-import, import-outside-toplevel
        check_mp_ver(min_msticpy_ver=mp_install_version)
    except RuntimeError:
        _disp_html("Installation skipped.")


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

    _disp_html("Checking msticpy version...<br>")
    wrong_ver_err = f"msticpy {mp_min_pkg_ver} or later is needed."
    inst_version = "none"
    try:
        import msticpy

        inst_version = _get_pkg_version(msticpy.__version__)
        if inst_version < mp_min_pkg_ver:
            raise ImportError(wrong_ver_err)

    except ImportError as err:
        _disp_html(
            MISSING_PKG_ERR.format(
                package="msticpy",
                inst_ver=inst_version,
                req_ver=mp_min_pkg_ver,
            )
        )
        resp = input("Install now? (y/n)")  # nosec
        if resp.casefold().startswith("y"):
            raise

        _disp_html(
            MP_INSTALL_FAILED.format(
                pkg="msticpy",
                ver=mp_min_pkg_ver,
                curr_ver=inst_version,
                nbk_uri=AZ_GET_STARTED,
            )
        )
        raise RuntimeError(wrong_ver_err) from err

    _disp_html(f"Info: msticpy version {mp_min_pkg_ver} OK<br>")


def _install_mp(mp_install_version, exact_version, extras, quiet=True):
    """Try to install MSTICPY."""
    sp_args = ["install", "--no-input"]
    if quiet:
        sp_args.append("--quiet")
    pkg_op = "==" if exact_version else ">="
    mp_pkg_spec = f"msticpy[{','.join(extras)}]" if extras else "msticpy"
    mp_pkg_spec = f"{mp_pkg_spec}{pkg_op}{mp_install_version}"
    sp_args.append(mp_pkg_spec)

    _disp_html(
        f"<br>Running pip {' '.join(sp_args)} - this may take a few moments...<br>"
    )

    ip_shell = get_ipython()
    ip_shell.run_line_magic("pip", " ".join(sp_args))


def _get_pkg_version(version):
    if isinstance(version, str):
        return parse_version(version)
    elif isinstance(version, tuple):
        return parse_version(".".join(str(ver) for ver in version))
    raise TypeError(f"Unparseable type version {version}")


def _disp_html(text):
    display(HTML(text))


def get_aml_user_folder():
    """Return the root of the user folder."""
    user_path = Path("/")
    path_parts = Path(".").absolute().parts
    for idx, part in enumerate(path_parts):
        if part.casefold() == "users":
            user_path = user_path.joinpath(part).joinpath(path_parts[idx + 1])
            break
        user_path = user_path.joinpath(part)
    return user_path
