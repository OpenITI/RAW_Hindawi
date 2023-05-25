"""Scrape Hindawi epub and pdf files"""

import requests
import os
import re
from bs4 import BeautifulSoup
import time
import random

def download_page(url, outfp=None, overwrite=False, sleep_time=0):
    """Download an html page

    Args:
        url (str): url of the page
        outfp (str): path to the output file
        overwrite (bool): if False, the page will not be re-downloaded
             if a file with that name already exists
        sleep_time (float): number of seconds to wait after downloading
    """
    if not outfp:
        outfp = url.split('/')[-1]

    if not overwrite and os.path.exists(outfp):
        return outfp
    
    r = requests.get(url)
    with open(outfp, mode="w", encoding="utf-8") as file:
        file.write(r.text)

    if sleep_time:
        time.sleep(sleep_time)
    return outfp

def download_file(url, outfp=None, overwrite=False, sleep_time=0):
    """Download large files

    Args:
        url (str): url of the page
        outfp (str): path to the output file
        overwrite (bool): if False, the page will not be re-downloaded
             if a file with that name already exists
        sleep_time (float): number of seconds to wait after downloading
    """

    if not outfp:
        outfp = url.split('/')[-1]
        
    if not overwrite and os.path.exists(outfp):
        return outfp

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(outfp, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

    if sleep_time:
        time.sleep(sleep_time)
        
    return outfp

def extract_categories(home_fp):
    """extract the list of the categories from the home page

    Args:
        home_fp (str): path to the downloaded home page
    """
    cat_d = dict()
    with open(home_fp, mode="r", encoding="utf-8") as file:
        page = file.read()
        categories = re.findall("/books/categories/(\w+).+?(\d+)",
                                page, flags=re.DOTALL)
        for cat, count in categories:
            cat_d[cat] = int(count)
            print(cat, count)
    return cat_d

def download_category_pages(relevant_categories):
    """Download the category pages (which contain links to the book pages)

    Args:
        relevant_categories (str): list of category names
    """
    base_cat_url = "https://www.hindawi.org/books/categories"
    for cat in relevant_categories:
        cat_count = cat_d[cat]
        n_sub_pages = int(cat_count / 20) + 1
        print(cat, cat_count, n_sub_pages)
        for i in range(1, n_sub_pages+1):
            sub_page_url = f"{base_cat_url}/{cat}/{i}"
            print(sub_page_url)
            sub_page_fp = f"categories/{cat}_{i}.html"
            if not os.path.exists(sub_page_fp):
                sleep_time = 2+ (random.randint(1,40) / 10)
                download_page(sub_page_url, sub_page_fp, sleep_time=sleep_time)

def download_books(download_epub=True, download_pdf=False, overwrite=False):
    """Download all books referenced in the downloaded category pages."""
    book_base_url = "https://downloads.hindawi.org/books"
    # open each downloaded category file: 
    for fn in os.listdir("categories"):
        print(fn)
        fp = os.path.join("categories", fn)
        with open(fp, mode="r", encoding="utf-8") as file:
            html = file.read()
            soup = BeautifulSoup(html)
            # get the links to all books listed on the page:
            books = soup.find_all("li", "bookCover")
            for book in books:
                # get the book's ID number:
                book_link = book.a["href"]
                book_id = re.findall("\d+", book_link)[0]

                # download the epub file:
                if download_epub:
                    epub_url = f"{book_base_url}/{book_id}.epub"
                    epub_fp = f"epub/{book_id}.epub"
                    sleep_time = 2+ (random.randint(1,40) / 10)
                    print(epub_url, epub_fp)
                    download_file(epub_url, epub_fp, overwrite=overwrite,
                                  sleep_time=sleep_time)
                
                # download the pdf file:
                if download_pdf:
                    pdf_url = f"{book_base_url}/{book_id}.pdf"
                    pdf_fp = f"pdf/{book_id}.pdf"
                    sleep_time = 2+ (random.randint(1,40) / 10)
                    download_file(pdf_url, pdf_fp, overwrite=overwrite,
                                  sleep_time=sleep_time)


# first, download the page that contains all the categories of the books:
home_page = "https://www.hindawi.org/books/"
home_fp = "home_page.html"
download_page(home_page, home_fp)


# then, extract the categories from the downloaded page:
cat_d = extract_categories(home_fp)


# Manually select the relevant categories:
relevant_categories = """\
literature
religions
history
geography
novels
biographies
poetry
linguistics
philosophy
arts
plays""".split("\n")

irrelevant_categories = """\
business
economics
technology
politics
health
psychology
science""".split("\n")

# download all pages for the relevant categories:
download_category_pages(relevant_categories)

# download the books from the relevant categories:
download_books(download_epub=True, download_pdf=False, overwrite=False)
