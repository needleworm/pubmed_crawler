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
import pyexcel as px
import time


class ChemCrawler:
    def __init__(self, keyword):
        self.keyword = keyword
        self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(keyword)
        self.chem_matrix = self.process_matrix()

    def make_csv_single_chem(self, outfile=None):
        if not outfile:
            outfile = "[frequency]" + self.keyword + ".csv"
        header = "Compound ID, Name, Frequency"

        ofile = open(outfile, 'w')
        ofile.write(header)

        for i in range(len(self.chem_list)):
            compound_id = self.chem_list[i]
            name = self.name_dict[compound_id].replace(",", "*")
            frequency = str(self.chem_matrix[i, i])
            ofile.write("\n" + compound_id + ", " + name + ", " + frequency)

        ofile.close()

        print("Result Saved as a CSV File")

    def process_matrix(self):
        num_chem = len(self.chem_list)
        matrix = np.zeros((num_chem, num_chem), dtype=np.int)

        for chem_json in self.chem_json_list:
            keys = list(chem_json.keys())

            IDXs = []

            for el in keys:
                idx = self.chem_list.index(el)
                matrix[idx, idx] += 1
                IDXs.append(idx)

            for i, j in itertools.permutations(IDXs, 2):
                matrix[i, j] += 1

        return matrix

    def process_pubmed_chem_info(self, keyword):
        chem_json_list = P.crawl_chem_json(keyword, silence=True)
        chem_list = []
        name_dict = {}

        for chem_json in chem_json_list:
            for chem in chem_json.keys():
                if chem not in chem_list:
                    chem_list.append(chem)
                    name_dict[chem] = chem_json[chem]["substance_name"]

        print("Total Number of Crawled Papers : " + str(chem_json_list))
        print("Total Number of Chemicals : " + str(chem_list))

        return chem_json_list, chem_list, name_dict
