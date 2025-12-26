from PyQt5 import QtWidgets
from gui.app import SurfaceApp

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SurfaceApp()
    window.show()
    sys.exit(app.exec_())