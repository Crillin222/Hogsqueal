import sys
import resources_rc
resources_rc.qInitResources()  # <-- Força o registro do resource

from PySide6.QtWidgets import QApplication, QToolButton
from PySide6.QtGui import QIcon

app = QApplication(sys.argv)
btn = QToolButton()
btn.setIcon(QIcon(":/icons/test.png"))
btn.setText("Sun")
btn.show()
app.exec()