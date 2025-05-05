
# === preparations start ===

# ensure that all libraries are found
# do this by initializing the required
# modules, so that they load all dependencies

# needed for libpyside6.abi3.so.X.Y to be found
import PySide6.QtWidgets


# Add the current dir of this file
# to the module search path
import sys
from os.path import dirname
sys.path.append(dirname(__file__))

# needed for libic4core.so to be found
# we do not want to call import imagingcontrol4
# as that is not sufficient for libic4core to be found
# we do not want to call ic4.Library.init() or similar
# as that is something that might lead to weird behavior

import os
import ctypes

def _package_path(*paths: str,
                  package_directory: str = os.path.dirname(os.path.abspath(__file__))):
    return os.path.join(package_directory, *paths)


if os.name != "nt":
    lib_name = "libic4core.so"
    fallback_path = [
        f"{dirname(__file__)}/../imagingcontrol4/{lib_name}",
    ]
    try:
        lib_path = _package_path(lib_name)
        ctypes.CDLL(lib_path)
    except (FileNotFoundError, OSError):
        c = None
        for fp in fallback_path:
            try:
                c = ctypes.CDLL(fp)
                if c:
                    break
            except (FileNotFoundError, OSError):
                pass
        if not c:
            raise FileNotFoundError(f"Unable to find {lib_name}")
        del c

# === preparations end ===

# Load everything we need from our wrapper library
# this implies that we can load from our current directory
from imagingcontrol4pyside6lib import DeviceSelectionDialog, PropertyDialog

# declare all memeber of imagingcontrol4pyside6
__all__ = ["DeviceSelectionDialog", "PropertyDialog"]
