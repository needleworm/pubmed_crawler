"""
Author : Byunghyun Ban
Last Modification : 2020.08.19.
halfbottle@sangsang.farm
https://github.com/needleworm
"""
from metapub import PubMedFetcher
from tqdm import tqdm


def remove_escape(string):
    retval = ""
    for el in string:
        if el not in "\n\t":
            retval += el
        else:
            retval += " "
    return retval


def crawl_chem_abstract(keyword, retmax=300, pyqt_text_browser=None):
    fetch = PubMedFetcher()

    pmids = fetch.pmids_for_query(keyword, retmax=retmax)

    print("PMID scan Done!")
    if pyqt_text_browser:
        pyqt_text_browser.append("PMID Scan Done!")

    json_dicts = []
    print("Crawling Paper Info..")
    if pyqt_text_browser:
        pyqt_text_browser.append("Crawling Paper Info..")

    for i, pmid in enumerate(pmids):
        try:
            article = fetch.article_by_pmid(pmid)
        except:
            print("Error reading " + str(pmid))
            if pyqt_text_browser:
                pyqt_text_browser.append("Error reading " + str(pmid))
            continue

        chemical = article.chemicals
        if not chemical:
            continue

        abstract = article.abstract.replace(",", "*")
        if not abstract:
            continue
        elif "\t" in abstract or "\n" in abstract:
            abstract = remove_escape(abstract)

        title = article.title
        if not title:
            continue
        elif "\t" in title or "\n" in title:
            title = remove_escape(title)

        chemical["title"] = title
        chemical["abstract"] = abstract

        json_dicts.append(chemical)

    print("Process Done!")
    if pyqt_text_browser:
        pyqt_text_browser.append("Progress Done!")
    return json_dicts


def crawl_chem_json(keyword, retmax=300, pyqt_text_browser=None):
    fetch = PubMedFetcher()

    pmids = fetch.pmids_for_query(keyword, retmax=retmax)
    print("PMID scan Done!")
    if pyqt_text_browser:
        pyqt_text_browser.append("PMID Scan Done!")

    json_dicts = []
    print("Crawling Paper Info..")
    if pyqt_text_browser:
        pyqt_text_browser.append("Crawling Paper Info..")

    for i, pmid in enumerate(pmids):
        try:
            article = fetch.article_by_pmid(pmid)
        except:
            print("Error reading " + str(pmid))
            if pyqt_text_browser:
                pyqt_text_browser.append("Error reading " + str(pmid))
            continue

        chemical = article.chemicals
        if not chemical:
            continue

        json_dicts.append(chemical)

    print("Process Done!")
    if pyqt_text_browser:
        pyqt_text_browser.append("Progress Done!")
    return json_dicts


def crawl_abstract(keyword, outfile=None, max_iter=1000, has_chem_only=False):
    fetch = PubMedFetcher()

    pmids = fetch.pmids_for_query(keyword, retmax=max_iter)
    print("PMID scan Done!")

    if not outfile:
        outfile = "[Crawling Results]" + keyword + ".tsv"

    o_file = open(outfile, 'w', encoding="utf8")

    header = "PMID\tAuthors\tYear\tTitle\tAbstract\tURL\tCitation\tChemicals\n"
    o_file.write(header)

    print("Crawling Paper Info..")

    for i, pmid in tqdm(pmids):
        article = fetch.article_by_pmid(pmid)
        if not article:
            continue

        authors = article.authors_str
        if not authors:
            continue
        elif "\t" in authors or "\n" in authors:
            authors = remove_escape(authors)

        year = article.year
        if not year:
            continue
        elif "\t" in year or "\n" in year:
            year = remove_escape(year)

        title = article.title
        if not title:
            continue
        elif "\t" in title or "\n" in title:
            title = remove_escape(title)

        abstract = article.abstract
        if not abstract:
            continue
        elif "\t" in abstract or "\n" in abstract:
            abstract = remove_escape(abstract)

        url = article.url
        if not url:
            continue
        elif "\t" in url or "\n" in url:
            url = remove_escape(url)

        citation = article.citation
        if not citation:
            continue
        elif "\t" in citation or "\n" in citation:
            citation = remove_escape(citation)

        chemical = article.chemicals
        if not chemical:
            if has_chem_only:
                continue
            chemical = "None"
        else:
            chemical = str(chemical).replace("\'", "\"")
            if "\t" in chemical or "\n" in chemical:
                chemical = remove_escape(chemical)

        o_file.write(pmid + "\t")
        o_file.write(authors + "\t")
        o_file.write(year + "\t")
        o_file.write(title + "\t")
        o_file.write(abstract + "\t")
        o_file.write(url + "\t")
        o_file.write(citation + "\t")
        o_file.write(chemical + "\n")

    o_file.close()
    print("Process Done!")
    print("Result is saved in <" + outfile + ">.")
