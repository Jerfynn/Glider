"""
GliderView - Desktop Underwater Glider Telemetry and 3D Orientation Viewer.
Entry point for the application.
"""

import sys
import os

# Redirect None stdout/stderr in windowed exe mode
if sys.stdout is None:
    class DummyStream:
        def write(self, s): pass
        def flush(self): pass
    sys.stdout = DummyStream()
if sys.stderr is None:
    class DummyStream:
        def write(self, s): pass
        def flush(self): pass
    sys.stderr = DummyStream()

# Set QtPy API preference
if "QT_API" not in os.environ:
    os.environ["QT_API"] = "pyside6"


# Disable strict PyOpenGL error checking for high performance and compatibility
try:
    import OpenGL
    OpenGL.ERROR_CHECKING = False
except Exception:
    pass

import qtpy
from qtpy import QtWidgets, QtCore, QtGui


def main():
    # High DPI Scaling configuration (Qt 5 compatibility, Qt 6 enables natively)
    if hasattr(qtpy, "QT_VERSION") and qtpy.QT_VERSION.startswith("5"):
        if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    # Configure OpenGL Surface Format for 3D Viewport compatibility on Windows
    gl_format = QtGui.QSurfaceFormat()
    gl_format.setDepthBufferSize(24)
    gl_format.setStencilBufferSize(8)
    gl_format.setSamples(4)  # 4x Multi-Sample Anti-Aliasing (MSAA)
    gl_format.setVersion(2, 1)
    gl_format.setProfile(QtGui.QSurfaceFormat.CompatibilityProfile)
    QtGui.QSurfaceFormat.setDefaultFormat(gl_format)

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("GliderView")
    app.setOrganizationName("OceanRobotics")

    from app.views.main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec_() if hasattr(app, "exec_") else app.exec())


if __name__ == "__main__":
    main()
