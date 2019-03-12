#! /usr/bin/python3

import sys
from os import listdir

from xml.dom.minidom import parse
from nltk.tokenize import word_tokenize

effect_clues = ["administered", "concurrently", "concomitantly", "increase", "increases", "increased", "effect",
                "effects", "prevent", "prevents", "prevented", "potentiate", "potentiates", "potentiated"]
mechanism_clues = ["reduce", "reduces", "reduced", "decrease", "decreases", "decreased", "change", "changes", "changed",
                   "elevate", "elevates", "elevated", "interfere", "interferes", "interfered"]


## -------------------
## -- check if a pair has an interaction, of which type

def check_interaction(tokens, entities, e1, e2, pair):
    e1_end = int(entities[e1][-1])
    e2_start = int(entities[e2][0])

    for t in tokens:
        tk_word = t[0]
        tk_start = t[1]
        tk_end = t[2]
        if tk_start > e1_end and tk_end < e2_start:
            # the token is between both entities
            # check if it is a word indicating interaction
            if tk_word.lower() in effect_clues:
                return "1", "effect"
            elif tk_word.lower() in mechanism_clues:
                return "1", "mechanism"

    return "0", "null"


## --------- tokenize sentence ----------- 
## -- Tokenize sentence, returning tokens and span offsets

def tokenize(txt):
    offset = 0
    tks = []
    for t in word_tokenize(txt):
        offset = txt.find(t, offset)
        tks.append((t, offset, offset + len(t) - 1))
        offset += len(t)
    return tks


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  baseline-NER-2.py target-dir
## --
## -- Extracts Drug NE from all XML files in target-dir
## --


# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in listdir(datadir):

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir + "/" + f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences:
        sid = s.attributes["id"].value  # get sentence id
        stext = s.attributes["text"].value  # get sentence text

        tokens = tokenize(stext)

        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents:
            id = e.attributes["id"].value
            offs = e.attributes["charOffset"].value.split("-")
            entities[id] = offs

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
        for p in pairs:
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            (is_ddi, ddi_type) = check_interaction(tokens, entities, id_e1, id_e2, p)
            print(sid + "|" + id_e1 + "|" + id_e2 + "|" + is_ddi + "|" + ddi_type)
