"""
PubMed Chemicals and Paper Crawler
with GUI
Byunghyun Ban
https://github.com/needleworm
"""
import chem_crawler as c
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets as Q


ui_class = uic.loadUiType("crawler_gui.ui")


class WindowClass(Q.QMainWindow, ui_class[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.progressBar.setValue(0)

        self.lineEdit.returnPressed.connect(self.button_pressed)
        self.pushButton.clicked.connect(self.button_pressed)

    def button_pressed(self):
        self.keyword = self.lineEdit.text()
        self.textBrowser.clear()
        self.textBrowser.append("Process Start!!")
        self.textBrowser.append("Keyword : " + self.keyword)
        c.ChemCrawler(self.keyword, with_abstract=self.checkBox.isChecked(),
                      pyqt_progress_bar=self.progressBar, pyqt_text_browser=self.textBrowser)


if __name__ == "__main__":
    app = Q.QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
