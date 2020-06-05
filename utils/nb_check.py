# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Checker for Python and msticpy versions."""
import os
import sys
from pathlib import Path
from time import sleep
from typing import Tuple
from binascii import hexlify
from IPython.display import display, clear_output, HTML


warn_mssg = []
err_mssg = []
MISSING_PKG_ERR = """
    <h3><font color='orange'>The package '<b>{package}</b>' is not
    installed or has an incorrect version</font></h3>
    <h4>Please install this now</h4>
    """
MIN_PYTHON_VER_DEF = (3, 6)
MSTICPY_REQ_VERSION = (0, 2, 7)
MAX_SETUP_WAIT = 240
LOCKFILE = "~/.mpnb.lock"
SETUP_LOG = "~/.nb.setup.log"
EXPECTED_LOG_LINES = 300


class ProgressBar(object):
    """Progress bar using HTML progress."""

    def __init__(self, capacity):
        self._display_id = hexlify(os.urandom(8)).decode('ascii')
        self.capacity = capacity
        self._progress = 0

    def _repr_html_(self):
        bar_html = (
            "<progress style='width:30%%' max='%d' value='%d'>"
            + "</progress> %d%% complete"
        )
        return bar_html % (self.capacity, self.progress, self.progress)

    def display(self):
        display(self, display_id=self._display_id)

    def update(self):
        display(self, display_id=self._display_id, update=True)

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()


def _html_out(text, font_col=None, bold=False):
    """Display HTML string with optional font color and bold."""
    out_html = text
    if font_col:
        out_html = "<font color='%s'>%s</font>" % (font_col, text)
    if bold:
        out_html = "<b>" + out_html + "</b>"
    display(HTML(out_html))


def _read_log_file_lines(file_name) -> int:
    log_file = Path(file_name).expanduser()
    if not log_file.exists():
        return 0
    with open(log_file, "r") as f_handle:
        return len(f_handle.readlines())


def check_container_install():
    """Check for current container setup and wait for completion."""
    p_bar = ProgressBar(100)

    _html_out("Checking for environment setup in progress...", bold=True)
    sleep(1)
    setup_finished = True
    if Path(LOCKFILE).expanduser().is_file():
        _html_out("Ongoing environment setup detected.", bold=True)
        _html_out("We recommend waiting for this to complete. (3-5 min)")
        p_bar.display()
        _html_out("""
            Type 'I','I' (or hit the kernel interrupt button) to stop waiting
            for this and continue with manual installation)
        """)
        setup_finished = False
    try:
        retry = True
        while retry:
            for _ in range(MAX_SETUP_WAIT):
                file_len = _read_log_file_lines(SETUP_LOG)
                p_bar.progress = int(100 * file_len / EXPECTED_LOG_LINES)
                if not Path(LOCKFILE).expanduser().is_file():
                    p_bar.progress = 100
                    setup_finished = True
                    break
                sleep(1)
            if setup_finished:
                break
            resp = input("Continue waiting (y/n)?")  # nosec
            if resp.casefold().startswith("n"):
                break

        clear_output()
        if not setup_finished:
            _html_out(
                "Container environment setup is not yet finished or may have stalled.",
                "orange"
            )
            _html_out("""
                We recommend that you re-run this cell.<br>
                Alternatively, you can proceed and install msticpy and its<br>
                dependencies from the notebook.<br>
                Note: if you do this, you may see some installation conflicts/warnings,
                although these are usually safe to ignore.
            """)
        else:
            _html_out("Environment setup has completed.", "green")
    except KeyboardInterrupt:
        clear_output()
        _html_out("\nInstallation wait interrupted.", "orange")
        _html_out("""
            Note: you may see some installation conflicts/warnings
            if you choose to proceed with installation from the
            notebook - these are usually safe to ignore.
        """)

    _html_out("Continuing wth notebook setup.")
    sleep(2)
    return setup_finished


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
    _html_out("Checking Python kernel version...")
    if sys.version_info < min_py_ver:
        _html_out(
            """
            <h3><font color='red'>This notebook requires a different notebook
            (Python) kernel version.</h3></font>
            From the Notebook menu (above), choose <b>Kernel</b> then
            <b>Change Kernel...</b> from the menu.<br>
            Select a <b>Python %s.%s</b> (or later) version kernel and then re-run
            this cell.<br><br>
            """ % min_py_ver
        )
        _html_out(
            """
            Please see the <b><a href="./TroubleShootingNotebooks.ipynb">
            TroubleShootingNotebooks</a></b>
            in this folder for more information<br><br><hr>
            """
        )
        raise RuntimeError("Python %s.%s or later kernel is required." % min_py_ver)

    _html_out(
        "Python kernel version %s.%s.%s OK" % (
            sys.version_info[0], sys.version_info[1], sys.version_info[2]
        ),
        "green"
    )


def check_mp_ver(min_msticpy_ver=MSTICPY_REQ_VERSION):
    """
    Check the current version of MSTICPY.

    Parameters
    ----------
    min_py_ver : Tuple[int, int]
        Minimum Python version

    Raises
    ------
    ImportError
        If the required version of msticpy cannot be imported.
    RuntimeError
        If the user opts not to install/upgrade msticpy.

    """
    check_container_install()
    _html_out("Checking msticpy version...")
    try:
        import msticpy  # pylint: disable=import-outside-toplevel
        mp_version = tuple([int(v) for v in msticpy.__version__.split(".")])
        if mp_version < min_msticpy_ver:
            raise ImportError("msticpy %s.%s.%s or later is needed." % min_msticpy_ver)

    except ImportError:
        _html_out(MISSING_PKG_ERR.format(package="msticpy"))
        sleep(1)
        resp = input("Install? (y/n)")  # nosec
        if resp.casefold().startswith("y"):
            raise ImportError("Install msticpy")

        _html_out(
            """
            <h3><font color='red'>The notebook cannot be run without
            the correct version of '<b>%s</b>' (%s.%s.%s or later)
            </font></h3>
            Please see the <b><a href="./TroubleShootingNotebooks.ipynb">
            TroubleShootingNotebooks</a></b>
            in this folder for more information<br><br><hr>
            """ % ("msticpy", *min_msticpy_ver)
        )
        raise RuntimeError("msticpy %s.%s.%s or later is required." % min_msticpy_ver)
    _html_out("msticpy version %s.%s.%s OK" % mp_version)
