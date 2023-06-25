import re, json
import openiti

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

### OpenITI functions
from openiti.helper.ara import deNoise, normalize_ara_light

### Variables

hindawi_metadata_file = 'hindawi_metadata_man_2023-05-26.tsv'
sourceFolder = "./epub/"
target_folder = "./converted_mARkdownSimple/"

splitter = "#META#Header#End#"




import os
import csv

def load_tsv_into_dict(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        data_dict = {row['BookID'] + ".epub": row for row in reader}
    return data_dict

hindawi_dict = load_tsv_into_dict(hindawi_metadata_file)

#print(hindawi_dict)


def get_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file name starts with 4 digits
            if re.match(r'\d+\.epub', file):
                file_list.append(os.path.join(root, file))
    return file_list


# text += '\n'.join(bs.stripped_strings) + "\n\n\n" --- this will get text out of tagged

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    text = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            bs = BeautifulSoup(item.get_content(), 'html.parser')

            # list of classes to remove
            classes_to_remove = ["footnote", "footnote_line", "copyright"] #
            for class_name in classes_to_remove:
                for elem in bs.find_all(class_=class_name):
                    elem.decompose()

            # reformat headers
            for elem in bs.find_all(['h1', 'h2', 'h3']):
                # add "# |" in front of the text of the element
                # <br> is necessary, otherwise \n are not inserted, for some reason...
                elem.string = "<br>\n\n\n# | %s \n\n\n<br>" % elem.text
                # replace the tag with its contents
                elem.unwrap()

            text += '\n'.join(bs.stripped_strings) + "\n\n\n"
            #text += str(bs) + "\n"

            #text += '\n'.join(bs.stripped_strings) + "\n\n\n"
    return text


def cleanText(doc):
    splitter = "#META#Header#End#"
    doc = doc.split(splitter)[1]
    doc = deNoise(doc) # remove short vowels...
    doc = normalize_ara_light(doc) # normalize arabic text...
    doc = re.sub("</?[a-z][^>]+>", " ", doc)
    doc = re.sub('[a-zA-Z]', ' ', doc)
    doc = re.sub('\W+', ' ', doc)
    doc = re.sub('\d+', ' ', doc)
    doc = re.sub('_+', ' ', doc)
    doc = re.sub(' +', ' ', doc)
    doc = doc.strip()
    return(doc)


# example usage

tsvData = ["fileName\tfolder\ttokens"]

counter = 0

# for file in get_all_files(sourceFolder):
#     print(file)
#     fileName = file.split("/")[-1]
#     folder = file.split("/")[-2]
#     with open(file, "r", encoding = "utf8") as f1:
#         text = f1.read()
#         if "#META#Header#End#" in text:
#             pass
#         else:
#             os.system("open -a KATE %s" % file)
#             print("#META#Header#End#")
#             input(file)

# input("The files must be fixed")


files_to_process = get_all_files(sourceFolder)
#files_to_process = ["/Users/romanov/_OpenITI/RAW_Hindawi/epub/71716470.epub"] # 0255Jahiz.BayanWaTabyin.Hindawi71716470


for file in files_to_process:
    fileName = file.split("/")[-1]
    if fileName in hindawi_dict:
        #print(file)
        print(fileName, " --- ", hindawi_dict[fileName]['BookURI'])

        text = extract_text_from_epub(file)
        text = deNoise(text)
        text = re.sub(r"\n(\w)", r"\n\n\1", text)
        text = re.sub(r"\n(   +)", r"\n", text)
        text = re.sub("<br>", "", text)

        meta = json.dumps(hindawi_dict[fileName], indent=4, ensure_ascii = False)

        text = "######OpenITI#\n\n\n%s\n\n\n#META#Header#End#\n\n\n" % meta + text

        file_openITI = hindawi_dict[fileName]['BookURI'] + "-ara1"

        with open(target_folder + file_openITI, "w", encoding = "utf8") as f9:
            f9.write(text)

    #input(file_openITI)



    # with open(file, "r", encoding = "utf8") as f1:
    #     text = f1.read()
    #     text_clean = cleanText(text)
    #     tokens = len(re.findall(r'\w+', text))

    #     row = "%s\t%s\t%d" % (fileName, folder, tokens)
    #     tsvData.append(row)


    # counter += 1
    # if counter % 100 == 0:
    #     print(counter)










