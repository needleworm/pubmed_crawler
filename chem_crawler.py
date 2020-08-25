"""
Author : Byunghyun Ban
Last Modification
2020.08.24.
https://github.com/needleworm
halfbottle@sangsang.farm
"""
import numpy as np
import pmcrawl as P
import itertools


class ChemCrawler:
    def __init__(self, keyword, with_abstract=False, pyqt_text_browser=None):
        self.keyword = keyword
        self.with_abstract = with_abstract
        self.pyqt_text_browser = pyqt_text_browser
        if not self.with_abstract:
            try:
                self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(keyword)
            except TimeoutError:
                print("Please Check Internet Connection! Retrying!")
                if self.pyqt_text_browser:
                    self.pyqt_text_browser.append("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(keyword)
        else:
            try:
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(keyword)
            except TimeoutError:
                print("Please Check Internet Connection! Retrying!")
                if self.pyqt_text_browser:
                    self.pyqt_text_browser.append("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(keyword)

        self.chem_matrix = self.process_matrix()
        self.make_csv_single_chem()

    def make_csv_single_chem(self, outfile=None):
        if not outfile:
            if self.with_abstract:
                outfile = "[with_abstract] " + self.keyword + ".csv"
            else:
                outfile = "[frequency] " + self.keyword + ".csv"
        header = ["Compound ID", "Name", "Frequency"]

        if self.with_abstract:
            header.append("Title")
            header.append("Abstract")

        ofile = open(outfile, 'w', encoding="utf8")
        ofile.write(", ".join(header))

        for i in range(len(self.chem_list)):
            compound_id = self.chem_list[i]
            name = self.name_dict[compound_id].replace(",", "*")
            frequency = str(self.chem_matrix[i, i])
            contents = [compound_id, name, frequency]
            if self.with_abstract:
                title = self.title_list[i]
                abstract = self.abstract_list[i]
                contents.append(title)
                contents.append(abstract)

            ofile.write("\n" + ", ".join(contents))

        ofile.close()

        print("Result Saved as a CSV File")
        if self.pyqt_text_browser:
            self.pyqt_text_browser.append("Result Saved as a CSV File")

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
        chem_json_list = P.crawl_chem_json(keyword, pyqt_text_browser=self.pyqt_text_browser)
        chem_list = []
        name_dict = {}

        for chem_json in chem_json_list:
            for chem in chem_json.keys():
                if chem not in chem_list:
                    chem_list.append(chem)
                    name_dict[chem] = chem_json[chem]["substance_name"]

        print("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        print("Total Number of Chemicals : " + str(len(chem_list)))
        if self.pyqt_text_browser:
            self.pyqt_text_browser.append("Total Number of Crawled Papers : " + str(len(chem_json_list)))
            self.pyqt_text_browser.append("Total Number of Chemicals : " + str(len(chem_list)))

        return chem_json_list, chem_list, name_dict

    def process_pubmed_chem_abstract_info(self, keyword):
        chem_json_list = P.crawl_chem_abstract(keyword, pyqt_text_browser=self.pyqt_text_browser)
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
        if self.pyqt_text_browser:
            self.pyqt_text_browser.append("Total Number of Crawled Papers : " + str(len(chem_json_list)))
            self.pyqt_text_browser.append("Total Number of Chemicals : " + str(len(chem_list)))

        return chem_json_list, chem_list, name_dict, title_list, abstract_list
