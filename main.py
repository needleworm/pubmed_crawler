"""
PubMed Chemicals and Paper Crawler
with GUI
Byunghyun Ban
https://github.com/needleworm
"""
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets as Q
from PyQt5.QtCore import *
from metapub import PubMedFetcher
import itertools
import numpy as np

ui_class = uic.loadUiType("resources/crawler_gui.ui")


class Crawl(QThread):
    progress_bar_value = pyqtSignal(int)
    textBrowser_value = pyqtSignal(str)

    def __init__(self, keyword, retmax, checkBox):
        QThread.__init__(self)
        self.keyword = keyword
        self.retmax = retmax
        self.checkBox = checkBox
        self.chem_json_list = []
        self.chem_list = []
        self.name_dict = []
        self.title_list = []
        self.abstract_list = []
        self.chem_matrix = []
        self.count = 5

    def run(self):
        if not self.checkBox:
            try:
                self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(self.keyword)
            except TimeoutError:
                print("Please Check Internet Connection! Retrying!")
                self.textBrowser_value.emit("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(self.keyword)
        else:
            try:
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(self.keyword)
            except TimeoutError:
                print("Please Check Internet Connection! Retrying!")
                self.textBrowser_value.emit("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(self.keyword)

        if self.chem_json_list:
            self.chem_matrix = self.process_matrix()
            self.make_csv_single_chem()
        else:
            print("No Result Found!")
            self.textBrowser_value.emit("No Result Found!")


    def crawl_chem_json(self, keyword, retmax=300):
        fetch = PubMedFetcher()

        pmids = fetch.pmids_for_query(keyword, retmax=retmax)

        print("Scanning Iteration : " + str(retmax))
        self.textBrowser_value.emit("Scanning Iteration : " + str(retmax))
        print("Expected Running Time : " + str(retmax * 2) + " seconds.")
        self.textBrowser_value.emit("Expected Running Time : " + str(retmax * 2) + " seconds.")

        print("PMID scan Done!")
        self.textBrowser_value.emit("PMID Scan Done!")
        self.progress_bar_value.emit(self.count)

        json_dicts = []
        print("Crawling Paper Info..")
        self.textBrowser_value.emit("Crawling Paper Info..")

        for i, pmid in enumerate(pmids):
            try:
                if int(i / len(pmids) * 100) > self.count:
                    self.count = int(i / len(pmids) * 100)
                    self.progress_bar_value.emit(self.count)
                try:
                    article = fetch.article_by_pmid(pmid)
                except:
                    print("Error reading " + str(pmid))
                    self.textBrowser_value.emit("Error reading " + str(pmid))
                    continue

                chemical = article.chemicals
                if not chemical:
                    continue

                json_dicts.append(chemical)
            except:
                continue

        print("Process Done!")
        self.textBrowser_value.emit("Progress Done!")
        return json_dicts

    def make_csv_single_chem(self, outfile=None):
        if not outfile:
            if self.checkBox:
                outfile = "[with_abstract] " + self.keyword + ".csv"
            else:
                outfile = "[frequency] " + self.keyword + ".csv"
        header = ["Compound ID", "Name", "Frequency"]

        if self.checkBox:
            header.append("Title")
            header.append("Abstract")

        ofile = open(outfile, 'w', encoding="utf8")
        ofile.write(", ".join(header))

        for i in range(len(self.chem_list)):
            compound_id = self.chem_list[i]
            name = self.name_dict[compound_id].replace(",", "*")
            frequency = str(self.chem_matrix[i, i])
            contents = [compound_id, name, frequency]
            if self.checkBox:
                title = self.title_list[i]
                abstract = self.abstract_list[i]
                contents.append(title)
                contents.append(abstract)

            ofile.write("\n" + ", ".join(contents))

        ofile.close()

        print("Result Saved as a CSV File")
        self.textBrowser_value.emit("Result Saved as a CSV File")
        print("Filename : " + outfile)
        self.textBrowser_value.emit("Filename : " + outfile)
        self.progress_bar_value.emit(100)

    def process_matrix(self):
        num_chem = len(self.chem_list)
        matrix = np.zeros((num_chem, num_chem), dtype=np.int)

        for chem_json in self.chem_json_list:
            keys = list(chem_json.keys())

            IDXs = []

            for el in keys:
                if el in "title abstract":
                    continue
                idx = self.chem_list.index(el)
                matrix[idx, idx] += 1
                IDXs.append(idx)

            for i, j in itertools.permutations(IDXs, 2):
                matrix[i, j] += 1

        return matrix

    def process_pubmed_chem_info(self, keyword):
        chem_json_list = self.crawl_chem_json(keyword, retmax=self.retmax)
        print("Crawling Done! Processing Output Files...")
        self.textBrowser_value.emit("Crawling Done! Processing Output Files...")
        chem_list = []
        name_dict = {}

        for chem_json in chem_json_list:
            for chem in chem_json.keys():
                if chem not in chem_list:
                    chem_list.append(chem)
                    name_dict[chem] = chem_json[chem]["substance_name"]

        print("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        print("Total Number of Chemicals : " + str(len(chem_list)))
        self.textBrowser_value.emit("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        self.textBrowser_value.emit("Total Number of Chemicals : " + str(len(chem_list)))

        return chem_json_list, chem_list, name_dict

    def process_pubmed_chem_abstract_info(self, keyword):
        chem_json_list = self.crawl_chem_abstract(keyword, retmax=self.retmax)
        print("Crawling Done! Processing Output Files...")
        self.textBrowser_value.emit("Crawling Done! Processing Output Files...")
        chem_list = []
        title_list = []
        abstract_list = []
        name_dict = {}

        for chem_json in chem_json_list:
            for key in chem_json.keys():
                if key in "title abstract":
                    continue

                if key not in chem_list:
                    chem_list.append(key)
                    title_list.append(chem_json["title"])
                    abstract_list.append(chem_json["abstract"])
                    name_dict[key] = chem_json[key]["substance_name"]

        print("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        print("Total Number of Chemicals : " + str(len(chem_list)))
        self.textBrowser_value.emit("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        self.textBrowser_value.emit("Total Number of Chemicals : " + str(len(chem_list)))

        return chem_json_list, chem_list, name_dict, title_list, abstract_list

    def crawl_chem_abstract(self, keyword, retmax=300):
        fetch = PubMedFetcher()
        self.progress_bar_value.emit(self.count)

        pmids = fetch.pmids_for_query(keyword, retmax=retmax)

        print("Scanning Iteration : " + str(retmax))
        self.textBrowser_value.emit("Scanning Iteration : " + str(retmax))
        print("Expected Running Time : " + str(retmax * 2) + " seconds.")
        self.textBrowser_value.emit("Expected Running Time : " + str(retmax * 2) + " seconds.")

        print("PMID scan Done!")
        self.textBrowser_value.emit("PMID Scan Done!")

        json_dicts = []
        print("Crawling Paper Info..")
        self.textBrowser_value.emit("Crawling Paper Info..")

        for i, pmid in enumerate(pmids):
            try:
                if int(i / len(pmids) * 100) > self.count:
                    self.count = int(i / len(pmids) * 100)
                    self.progress_bar_value.emit(self.count)

                try:
                    article = fetch.article_by_pmid(pmid)
                except:
                    print("Error reading " + str(pmid))
                    self.textBrowser_value.emit("Error reading " + str(pmid))
                    continue

                chemical = article.chemicals
                if not chemical:
                    continue

                abstract = article.abstract.replace(",", "*")
                if not abstract:
                    continue
                elif "\t" in abstract or "\n" in abstract:
                    abstract = abstract.replace("\t", " ")
                    abstract = abstract.replace("\n", " ")

                title = article.title
                if not title:
                    continue
                elif "\t" in title or "\n" in title:
                    title = title.replace("\t", " ")
                    title = title.replace("\n", " ")

                chemical["title"] = title
                chemical["abstract"] = abstract

                json_dicts.append(chemical)
            except:
                continue

        print("Process Done!")
        self.textBrowser_value.emit("Progress Done!")
        return json_dicts


class WindowClass(Q.QMainWindow, ui_class[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.lineEdit.returnPressed.connect(self.button_pressed)
        self.pushButton.clicked.connect(self.button_pressed)

    def button_pressed(self):
        self.keyword = self.lineEdit.text()
        self.retmax = self.spinBox.value()
        self.textBrowser.clear()
        self.textBrowser.append("Process Start!!")
        self.textBrowser.append("Keyword : " + self.keyword)
        self.th = Crawl(self.keyword, self.retmax, self.checkBox.isChecked())
        self.th.progress_bar_value.connect(self.progressBar.setValue)
        self.th.textBrowser_value.connect(self.textBrowser.append)
        self.th.start()


if __name__ == "__main__":
    app = Q.QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
