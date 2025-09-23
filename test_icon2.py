from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication
import sys

import resources_rc
resources_rc.qInitResources()  # <-- ESSENCIAL

app = QApplication(sys.argv)
svg = QSvgWidget(":/icons/sun.svg")
svg.show()
app.exec()