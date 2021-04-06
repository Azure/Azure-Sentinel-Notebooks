# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Checker for Python and msticpy versions."""
import importlib
import os
import sys

from IPython import get_ipython
from IPython.display import HTML, display
from pkg_resources import parse_version


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
    <h4><font color='red'>The notebook cannot be run without
    the correct version of '<b>{pkg}</b>' ({ver} or later).</font></h4>
    Please see the <a href="{nbk_uri}">
    Getting Started Guide For Azure Sentinel ML Notebooks</a></b>
    for more information<br><hr>
"""
MIN_PYTHON_VER_DEF = (3, 6)
MSTICPY_REQ_VERSION = (0, 9, 0)
VER_RGX = r"(?P<maj>\d+)\.(?P<min>\d+).(?P<pnt>\d+)(?P<suff>.*)"


def check_versions(
    min_py_ver=MIN_PYTHON_VER_DEF,
    min_mp_ver=MSTICPY_REQ_VERSION,
    extras=None,
    mp_release=None,
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
    print("Note: you may need to scroll down this cell to see the full output.")

    if isinstance(min_py_ver, str):
        min_py_ver = _get_pkg_version(min_py_ver).release
    check_python_ver(min_py_ver=min_py_ver)

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
            )
    except ImportError:
        _install_mp(
            mp_install_version=mp_install_version,
            exact_version=exact_version,
            extras=extras,
        )
        _disp_html(
            "Installation completed. Attempting to re-import/reload MSTICPy..."
        )
        # pylint: disable=unused-import, import-outside-toplevel
        if "msticpy" in sys.modules:
            importlib.reload(sys.modules["msticpy"])
        else:
            import msticpy
        # pylint: enable=unused-import, import-outside-toplevel
        check_mp_ver(min_msticpy_ver=mp_install_version)
    except RuntimeError:
        _disp_html("Installation aborted.")

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
        display(
            "Recommended: switch to using the 'Python 3.8 -AzureML' notebook kernel."
        )
    _disp_html(
        "Info: Python kernel version %s.%s.%s OK<br>"
        % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
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

    _disp_html("Checking msticpy version...<br>")
    wrong_ver_err = f"msticpy {mp_min_pkg_ver} or later is needed."
    inst_version = "none"
    try:
        import msticpy

        inst_version = _get_pkg_version(msticpy.__version__)
        if inst_version < mp_min_pkg_ver:
            raise ImportError(wrong_ver_err)

    except ImportError:
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
        raise RuntimeError(wrong_ver_err)

    _disp_html(f"Info: msticpy version {mp_min_pkg_ver} OK<br>")


def _install_mp(mp_install_version, exact_version, extras):
    """Try to install MSTICPY."""
    sp_args = ["install"]
    pkg_op = "==" if exact_version else ">="
    mp_pkg_spec = f"msticpy[{','.join(extras)}]" if extras else "msticpy"
    mp_pkg_spec = f"{mp_pkg_spec}{pkg_op}{mp_install_version}"
    sp_args.append(mp_pkg_spec)

    display(
        HTML(f"<br>Running pip {' '.join(sp_args)} - this may take a few moments...<br>")
    )

    ip_shell = get_ipython()
    ip_shell.run_line_magic("pip", " ".join(sp_args))


def _set_kql_env_vars(extras):
    jp_extended = ("azsentinel", "azuresentinel", "kql")
    # If running in
    if extras and any(extra for extra in extras if extra in jp_extended):
        os.environ["KQLMAGIC_EXTRAS_REQUIRES"] = "jupyter-extended"
    else:
        os.environ["KQLMAGIC_EXTRAS_REQUIRES"] = "jupyter-basic"


def _get_pkg_version(version):
    if isinstance(version, str):
        return parse_version(version)
    elif isinstance(version, tuple):
        return parse_version(".".join(str(ver) for ver in version))
    raise TypeError(f"Unparseable type version {version}")


def _disp_html(text):
    display(HTML(text))
