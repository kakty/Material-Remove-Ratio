from gui.app import SurfaceApp
from PyQt5 import QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SurfaceApp()
    window.show()
    sys.exit(app.exec_())