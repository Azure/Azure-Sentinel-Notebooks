# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Checker for Python and msticpy versions."""
import importlib
import os
import sys
import warnings
from IPython.display import display, clear_output, HTML, Markdown
from pathlib import Path
from time import sleep
from binascii import hexlify

warn_mssg = []
err_mssg = []
MISSING_PKG_ERR = """
    <h3><font color='orange'>The package '<b>{package}</b>' is not 
    installed or has an incorrect version</font></h3>
    <h4>Please install this now</h4>
    """
MIN_PYTHON_VER_DEF = (3, 6)
MSTICPY_REQ_VERSION = (0, 2, 7)
MAX_SETUP_WAIT = 160
LOCKFILE = "~/.mpnb.lock"


class ProgressBar(object):
    """Progress bar using HTML progress."""

    def __init__(self, capacity):
        self._display_id = hexlify(os.urandom(8)).decode('ascii')
        self.capacity = capacity
        self._progress = 0
        
    def _repr_html_(self):
        bar_html = "<progress style='width:30%%' max='%d' value='%d'></progress> %ss"
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

        
def html_out(text, font_col=None, bold=False):
    """Display HTML string with optional font color and bold."""
    out_html = text
    if font_col:
        out_html = "<font color='%s'>%s</font>" % (font_col, text)
    if bold:
        out_html = "<b>" + out_html + "</b>"
    display(HTML(out_html))

    
def check_container_install():
    """Check for current container setup and wait for completion."""
    bar = ProgressBar(MAX_SETUP_WAIT)

    html_out("Checking for environment setup in progress...", bold=True)
    sleep(1)
    if Path(LOCKFILE).expanduser().is_file():
        html_out("Ongoing environment setup detected.", bold=True)
        html_out("We recommend waiting for this to complete. (max 120s)")
        bar.display()
        html_out("Type 'I','I' (or hit the kernel interrupt button) to stop waiting for this and continue with manual installation)")

    try:
        cyc_count = 0
        for cyc_count in range(MAX_SETUP_WAIT):
            bar.progress = MAX_SETUP_WAIT - cyc_count
            if not Path(LOCKFILE).expanduser().is_file():
                break
            sleep(1)

        clear_output()
        if not cyc_count < MAX_SETUP_WAIT - 1:
            html_out("Container environment setup appears to have stalled.", "orange")
            html_out("Note: you may see some installation conflicts/warnings - these are usually safe to ignore.")
        else:
            html_out("Environment setup has completed.", "green")
    except KeyboardInterrupt:
        clear_output()
        html_out("\nInstallation wait interrupted.", "orange")
        html_out("Note: you may see some installation conflicts/warnings - these are usually safe to ignore.")

    html_out("Continuing wth notebook setup.")
    sleep(2)


def check_python_ver(min_py_ver=MIN_PYTHON_VER_DEF):
    """
    Checks the current version of the Python kernel.
    
    Parameters
    ----------
    min_py_ver : Tuple[int, int]
        Minimum Python version
        
    Raises
    ------
    RuntimeError
        If the Python version does not support the notebook.

    """
    html_out("Checking Python kernel version...")
    if sys.version_info < min_py_ver:
        html_out(
            """
            <h3><font color='red'>This notebook requires a different notebook
            (Python) kernel version.</h3></font>
            From the Notebook menu (above), choose <b>Kernel</b> then 
            <b>Change Kernel...</b> from the menu.<br>
            Select a <b>Python %s.%s</b> (or later) version kernel and then re-run
            this cell.<br><br>
            """ % min_py_ver
        )
        html_out(
            """
            Please see the <b><a href="./TroubleShootingNotebooks.ipynb">
            TroubleShootingNotebooks</a></b>
            in this folder for more information<br><br><hr>
            """
        )
        raise RuntimeError("Python %s.%s or later kernel is required." % min_py_ver)

    html_out(
        "Python kernel version %s.%s.%s OK" % (
            sys.version_info[0], sys.version_info[1], sys.version_info[2]
        ),
        "green"
    )

def check_mp_ver(min_msticpy_ver=MSTICPY_REQ_VERSION):
    """
    Checks the current version of .
    
    Parameters
    ----------
    min_py_ver : Tuple[int, int]
        Minimum Python version
        
    Raises
    ------
    RuntimeError
        If the Python version does not support the notebook.

    """
    check_container_install()
    html_out("Checking msticpy version...")
    try:
        import msticpy
        mp_version = tuple([int(v) for v in msticpy.__version__.split(".")])
        if mp_version < min_msticpy_ver:
            raise ImportError("msticpy %s.%s.%s or later is needed." % min_msticpy_ver)
            
    except ImportError:
        html_out(MISSING_PKG_ERR.format(package="msticpy"))
        sleep(1)
        resp = input("Install? (y/n)")
        if resp.casefold().startswith("y"):
            raise ImportError("Install msticpy")
        else:
            html_out(
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
    html_out("msticpy version %s.%s.%s OK" % mp_version)