import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from arduino import ArduinoController
from ui import MainWindow

app = QApplication(sys.argv)
arduino = ArduinoController()
window = MainWindow(arduino)

# Load Font
font_id = QFontDatabase.addApplicationFont("PixelOperator.ttf")
if font_id != -1:
    family = QFontDatabase.applicationFontFamilies(font_id)[0]
    app.setFont(QFont(family))

# Load Theme
with open("theme.qss", "r") as f:
    app.setStyleSheet(f.read())

window.show()
sys.exit(app.exec_())
