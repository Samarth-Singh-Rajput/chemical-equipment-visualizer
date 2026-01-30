from PyQt5.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel('PyQt5 is working!')
label.show()
app.exec_()
