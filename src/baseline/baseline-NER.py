#! /usr/bin/python3

import sys
from os import listdir

from xml.dom.minidom import parse
from nltk.tokenize import word_tokenize

## ------------------- 
## -- check if a token is a drug, and of which type

suffixes = ["idase", "idone", "uride", "ogens", "rinol", "amate", "lones", "pamil", "olone", "parin", "ssant", "udine",
            "D", "etron", "adiol", "feine", "pines", "zines", "toxin", "MAO", "opram", "ophen", "sides", "talis",
            "ulant", "ylate", "osine", "oxide", "caine", "illin", "itant", "limus", "pride", "sulin", "oride", "abine",
            "hrine", "iazem", "atory", "oidal", "emide", "hanol", "phine", "SAIDs", "coxib", "necid", "nists", "esium",
            "acids", "nolol", "nafil", "azine", "exate", "rates", "cking", "lcium", "azide", "zepam", "arone", "rofen",
            "ampin", "ergic", "roids", "tamin", "adine", "odium", "bital", "pirin", "lants", "orine", "mines", "zolam",
            "apine", "cohol", "ckers", "ipine", "acid", "yclic", "otics", "tives", "xacin", "etine", "epine", "drugs",
            "tatin", "thium", "lline", "amide", "sants", "etics", "itors", "ytoin", "gents", "navir", "goxin", "farin",
            "mycin", "idine", "amine", "azole"]


def load_suffixes_5():
    loaded = {}
    for k in ["brand", "drug", "group", "drug_n"]:
        with open('/Users/lluccardoner/PycharmProjects/MET_AHLT_Lab_2019/src/data/' + k + '_suffix_5_DrugBank.txt',
                  'r') as f:
            loaded[k] = f.read().splitlines()
    return loaded


type_suffixes = load_suffixes_5()


def classify_token(txt):
    if txt.isupper():
        return True, "brand"
    elif txt[-5:] in suffixes:
        return True, "drug"
    else:
        return False, ""


def classify_token_2(txt):
    if txt.isupper():
        return True, "brand"
    elif txt[-5:] in suffixes:
        return True, "drug"
    elif txt[-1:] == "s":
        return True, "group"
    else:
        return False, ""


def classify_token_3(txt):
    if txt.isupper() or txt[-5:].lower() in type_suffixes["brand"]:
        return True, "brand"
    elif txt[-5:].lower() in type_suffixes["drug"]:
        return True, "drug"
    elif txt[-5:].lower() in type_suffixes["group"]:
        return True, "group"
    elif txt[-5:].lower() in type_suffixes["drug_n"]:
        return True, "drug_n"
    else:
        return False, ""


## --------- tokenize sentence -----------
## -- Tokenize sentence, returning tokens and span offsets

def tokenize(txt):
    offset = 0
    tks = []
    for t in word_tokenize(txt):
        offset = txt.find(t, offset)
        tks.append((t, offset, offset + len(t)))
        offset += len(t)
    return tks


## --------- Entity extractor -----------
## -- Extract drug entities from given text and return them as
## -- a list of dictionaries with keys "offset", "text", and "type"

def extract_entities(stext, classifier="1"):
    result = []
    tokens = tokenize(stext)

    prev_drug = False
    for t in tokens:
        tokenTxt = t[0]

        if classifier == "1":
            (is_drug, tk_type) = classify_token(tokenTxt)
        elif classifier == "2":
            (is_drug, tk_type) = classify_token_2(tokenTxt)
        elif classifier == "3":
            (is_drug, tk_type) = classify_token_3(tokenTxt)
        else:
            print("No classifier", classifier)
            exit(1)

        if not is_drug and not prev_drug:
            # non-drug token after a non-drug token.
            # Nothing to do, just skip the token
            continue

        elif is_drug and not prev_drug:
            # Is a drug token after a non-drug. Start of drug name.
            # Remember offset start/end and drug type
            drug_start = t[1]
            drug_end = t[2]
            drug_type = tk_type
            prev_drug = True

        elif is_drug and prev_drug:
            # Is a drug token after a drug token.
            # Continuation of drug name. Update offset end
            drug_end = t[2]
            prev_drug = True

        elif not is_drug and prev_drug:
            # non-drug after a drug token.
            # The drug name ended, output it
            e = {"offset": str(drug_start) + "-" + str(drug_end),
                 "text": stext[drug_start:drug_end],
                 "type": drug_type}
            result.append(e)
            prev_drug = False

    return result


## --------- MAIN PROGRAM -----------
## --
## -- Usage:  baseline-NER.py target-dir
## --
## -- Extracts Drug NER from all XML files in target-dir
## --


# directory with files to process
datadir = sys.argv[1]
classifier = sys.argv[2]

# process each file in directory
for f in listdir(datadir):

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir + "/" + f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences:
        sid = s.attributes["id"].value  # get sentence id
        stext = s.attributes["text"].value  # get sentence text

        # extract entities in text
        entities = extract_entities(stext, classifier)

        # print sentence entities in format requested for evaluation
        for e in entities:
            print(sid + "|" + e["offset"] + "|" + e["text"] + "|" + e["type"])
