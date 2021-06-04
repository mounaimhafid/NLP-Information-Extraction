"""
Abdelmounaim Hafid axh170730
CS6320.003 NLP
Final Project: Information Extraction
"""
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from spacy import Language
import os
from nltk.corpus import wordnet
import re
import pprint as pp
from spacy import displacy
import json



doc1 = "articles/Amazon_com.txt"
test_doc = "test_input.txt"
ex_sent = "Abraham Lincoln was born on February 12, 1809, as the second child of Thomas and Nancy Hanks Lincoln, in a one-room log cabin on Sinking Spring Farm near Hodgenville, Kentucky."

#get the requried synsets
def getSynsets(word):

    synsets = wordnet.synsets(word)

    d = list()
    for set in synsets:
        hypernyms = list()
        hyponyms = list()
        meronyms = list()
        holonyms = list()
        name = set.lemma_names()
        for n in set.hypernyms():
            hypernyms.append(n.lemma_names())
        for n in set.hyponyms():
            hyponyms.append(n.lemma_names())
        for n in set.part_meronyms():
            meronyms.append(n.lemma_names())
        for n in set.part_holonyms():
            holonyms.append(n.lemma_names())
        tup = (name, hypernyms, hyponyms, meronyms, holonyms)
        d.append(tup)

    return word, d

#initialize pipeline
def init_pipe():

    nlp_pipeline = en_core_web_sm.load()

    #print(nlp_pipeline.pipe_names)

    return nlp_pipeline

#return pipeline
def feedToPipe(pipe: Language, docName):
    file = open(docName, encoding='utf-8')

    fileStr = file.read().replace("\n", " ")

    doc = pipe(fileStr)

    return doc


#return the tags in a sentence
def tagSent(sent):


    tagged = word_tokenize(sent)
    tagged = pos_tag(tagged)

    return tagged

#return the entities in a sentence
def entityRecog(sent):

    nlp = en_core_web_sm.load()
    entities = nlp(sent)
    for ent in entities.ents:
        print((ent.text, ent.label_))

#main function to detect part of relationships
def detectPartOfRelation(pipe: Language, sentence: str, output):
    p = init_pipe()
    doc = pipe(sentence)
    keywords = ['part of', 'in']
    lemmatized_sentence = list()
    nsubj = dict()  # noun subjects for some verb (key) (value is list of noun subjects)
    foundPart = False
    foundWhole = False
    tmp_Part = ""
    tmp_Whole = ""
    list_of_arguments = list()
    outFile1 = output
    for token in doc:
        lemmatized_sentence.append(token.lemma_)

    #search for some patterns:
    foundCity = False
    foundState = False
    pattern_city_state = r"\w+\s?,\s?\w+\s*\b"
    list_city_state = re.findall(pattern_city_state, sentence)
    #list_city_state = list(sum(list_city_state,()))
    print(list_city_state)
    for cityState in list_city_state:
        tmp = cityState
        for tok in doc:
            if tok.text == tmp[0]:
                if tok.ent_type_ == "GPE":
                    city = tok.text
                    foundCity = True
            if tok.text == tmp[1]:
                if tok.ent_type_ == "GPE":
                    state = tok.text
                    foundState = True
            if foundCity and foundState:
                if city == state:
                    continue
                argument_dict = \
                    {
                        "template": "PART",
                        "sentence": sentence,
                        "arguments":
                            {
                                "1": city,
                                "2": state
                            }
                    }
                list_of_arguments.append(argument_dict)
                pp.pprint("PARTOF({},{})".format(city, state), stream=outFile1)
            foundState = False
            foundCity = False

    #search for part of --> X is part of Y
    #list_part_of = re.findall(r"(\b)\w+(\s)+part\s+of(\s)+\w+(\b)",sentence)
    list_is_part_of = re.findall(r"\w+\sis\spart\sof\s\w+\b",sentence)
    foundPart = False
    foundW = False
    #print(list_part_of)
    print(list_is_part_of)
    for partWhole in list_is_part_of:
        tmp = partWhole
        for tok in doc:
            if tok.text == tmp[0]:
                if tok.ent_type_ == "ORG" or tok.ent_type_ == "GPE":
                    part = tok
                    foundPart = True
            if tok.text == tmp[1]:
                if tok.ent_type_ == "ORG" or tok.ent_type_ == "GPE":
                    whole = tok
                    foundW = True
            if foundPart and foundW:
                if part.ent_type_ == whole.ent_type_ == "ORG" or part.ent_type_ == whole.ent_type_ == "GPE":
                    text1 = part.text
                    text2 = whole.text
                    # for chunk in doc.noun_chunks:
                    #     if part.text in chunk.text:
                    #         text1 = chunk.text
                    #     if whole.text in chunk.text:
                    #         text2 = chunk.text
                    if text1 == text2:
                        continue
                    argument_dict = \
                        {
                            "template": "PART",
                            "sentence": sentence,
                            "arguments":
                                {
                                    "1": text1,
                                    "2": text2
                                }
                        }
                    list_of_arguments.append(argument_dict)
                    pp.pprint("PARTOF({},{})".format(text1, text2), stream=outFile1)
            foundW = False
            foundPart = False

    # for partWhole in list_part_of:
    #     tmp = partWhole.split("is part of")
    #     tmp[0] = tmp[0].strip()
    #     tmp[1] = tmp[1].strip()
    #     for tok in doc:
    #         if tok.text == tmp[0]:
    #             if tok.ent_type_ == "ORG" or tok.ent_type_ == "GPE" or tok.ent_type_ == "LOC":
    #                 part = tok.text
    #                 foundPart = True
    #         if tok.text == tmp[1]:
    #             if tok.ent_type_ == "ORG" or tok.ent_type_ == "GPE" or tok.ent_type_ == "LOC":
    #                 whole = tok.text
    #                 foundW = True
    #         if foundPart and foundW:
    #             pp.pprint("PARTOF({},{})".format(part, whole), stream=outFile1)
    #         foundW = False
    #         foundPart = False
    #
    for tok in doc:
        if tok.ent_type_ == "ORG" or tok.ent_type_ == "GPE":
            for possible_whole in tok.subtree:
                if possible_whole.dep_ == "prep" and (possible_whole.text == "in" or possible_whole.text == "of"):
                    for obj in possible_whole.subtree:
                        if obj.dep_ == "pobj":
                            if tok.ent_type_ == obj.ent_type_ == "ORG" or tok.ent_type_ == obj.ent_type_ == "GPE":
                                text1 = tok.text
                                text2 = obj.text
                                # for chunk in doc.noun_chunks:
                                #     if tok.text in chunk.text:
                                #         text1 = chunk.text
                                #     if obj.text in chunk.text:
                                #         text2 = chunk.text
                                argument_dict = \
                                    {
                                        "template": "PART",
                                        "sentence": sentence,
                                        "arguments":
                                            {
                                                "1": text1,
                                                "2": text2
                                            }
                                    }
                                list_of_arguments.append(argument_dict)
                                pp.pprint("PARTOF({},{})".format(text1, text2), stream=outFile1)

    return list_of_arguments

#main function to detect the buy relationship
def detectBuyRelation(pipe: Language, sentence: str, output):
    p = init_pipe()
    doc = pipe(sentence)
    keywords = ['bargain', 'buy', 'steal', 'purchase', 'get', 'acquire', 'buy back', 'repurchase', 'buy off', 'pay off']
    companies = ["Berkshire", "GEICO", "NRG"]
    months = ["January, February", "March", "April", "May", "June", "July", "August",\
              "September", "October", "November", "December"]
    lemmatized_sentence = list()
    verbs = list()
    nsubj = dict() #noun subjects for some verb (key) (value is list of noun subjects)
    date = dict()
    dobj = dict()
    list_of_arguments = list()
    foundNsubj = False
    foundDobj = False
    foundDate = False
    tmp_nsubj = ""
    tmp_dobj = ""
    tmp_date = ""
    outFile1 = output
    for token in doc:
        lemmatized_sentence.append(token.lemma_)
    #print(lemmatized_sentence)
    for possible_verb in doc:
        argument_dict = dict()
        if possible_verb.pos_ == "VERB" and possible_verb.lemma_ in keywords:
            for possible_nsubj in possible_verb.children:
                if possible_nsubj.dep_ == "nsubj" or possible_nsubj.dep_ == "nsubjpass" and (possible_nsubj.ent_type_ == "ORG" or possible_nsubj.text in companies):
                    verbs.append(possible_verb.text)
                    tmp_nsubj = possible_nsubj.text
                    foundNsubj = True
                    if possible_verb.text in nsubj:
                        nsubj[possible_verb.text].append(possible_nsubj.text)
                    else:
                        nsubj[possible_verb.text] = [possible_nsubj.text]

                    for possible_dobj in possible_verb.children:
                        if "dobj" in possible_dobj.dep_ and (possible_dobj.ent_type_ == "ORG" or possible_dobj.text in companies):
                            tmp_dobj = possible_dobj.text
                            foundDobj = True
                            if possible_verb in dobj:
                                dobj[possible_verb.text].append(possible_dobj.text)
                            else:
                                dobj[possible_verb.text] = [possible_dobj.text]
                    for possible_Date in possible_verb.subtree:
                        for obj in possible_Date.lefts:
                            if obj.ent_type_ == "DATE" or obj.text in months:
                                tmp_date = obj.text
                                foundDate = True
                                if possible_verb.text in date:
                                    date[possible_verb.text].append(obj.text)
                                else:
                                    date[possible_verb.text] = [possible_Date.text]
                        for obj in possible_Date.rights:
                            if obj.ent_type_ == "DATE" or obj.text in months:
                                tmp_date = obj.text
                                foundDate = True
                                if possible_verb.text in date:
                                    date[possible_verb.text].append(obj.text)
                                else:
                                    date[possible_verb.text] = [possible_Date.text]
                    # for possible_Date in possible_verb.rights:
                    #     if possible_Date.ent_type_ == "DATE" or possible_Date.text in months:
                    #         tmp_date = possible_Date.text
                    #         foundDate = True
                    #         if possible_verb.text in date:
                    #             date[possible_verb.text].append(possible_Date.text)
                    #         else:
                    #             date[possible_verb.text] = [possible_Date.text]
                    # for possible_Date in possible_verb.children:
                    #     if "prep" in possible_Date.dep_:
                    #         for word in possible_Date.children:
                    #             if word.ent_type_ == "DATE" or word.text in months:
                    #                 tmp_date = word.text
                    #                 foundDate = True
                    #                 if possible_verb.text in date:
                    #                     date[possible_verb.text].append(word.text)
                    #                 else:
                    #                     date[possible_verb.text] = [word.text]
        if foundDate and foundDobj and foundNsubj:
            for chunk in doc.noun_chunks:
                if chunk.root.text == tmp_nsubj:
                    tmp_nsubj = chunk.text
                if chunk.root.text == tmp_dobj:
                    tmp_dobj = chunk.text
                if chunk.root.text == tmp_date:
                    tmp_date = chunk.text
            argument_dict = \
                {
                    "template": "BUY",
                    "sentence": sentence,
                    "arguments":
                        {
                            "1": tmp_nsubj,
                            "2": tmp_dobj,
                            "3": tmp_date
                        }
                }
            list_of_arguments.append(argument_dict)
            pp.pprint("BUY({},{},{})".format(tmp_nsubj, tmp_dobj, tmp_date), stream=outFile1)
            foundNsubj = False
            foundDobj = False
            foundDate = False
    #check for noun phrases/chunks --> check if word is head of noun chunk.
    for chunk in doc.noun_chunks:
        for key,value in nsubj.items():
            if chunk.root.text in value:
                value.remove(chunk.root.text)
                value.append(chunk.text)
        for key,value in dobj.items():
            if chunk.root.text in value:
                value.remove(chunk.root.text)
                value.append(chunk.text)
        #print(chunk.text + "\t| " + chunk.root.text + "\t|" + chunk.root.dep_ + "\t|" + chunk.root.head.text)
    print(sentence)
    print(verbs)
    print(nsubj)
    print(date)
    print(dobj)
    return list_of_arguments

#main function to detect the born relationship
def detectBornRelation(pipe: Language, sentence: str, output):
    p = init_pipe()
    doc = pipe(sentence)
    keywords = ['bear', 'give birth', 'deliver', 'birth', 'founded', 'expect', 'born', "found"] #extracted from synsets
    #companies = ["Berkshire", "GEICO", "NRG"]
    months = ["January, February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]
    lemmatized_sentence = list()
    verbs = list()
    nsubj = dict() #noun subjects for some verb (key) (value is list of noun subjects)
    date = dict()
    loc = dict()
    list_of_arguments = list()
    foundNsubj = False
    foundLocation = False
    foundDate = False
    tmp_nsubj = ""
    tmp_loc = ""
    tmp_date = ""
    outFile1 = output
    for token in doc:
        lemmatized_sentence.append(token.lemma_)
    #print(lemmatized_sentence)
    for possible_verb in doc:
        argument_dict = dict()
        if possible_verb.pos_ == "VERB" and possible_verb.lemma_ in keywords:
            for possible_nsubj in possible_verb.children:
                if possible_nsubj.dep_ == "nsubj" or possible_nsubj.dep_ == "nsubjpass" and (possible_nsubj.ent_type_ == "ORG" or possible_nsubj.ent_type_ == "PERSON" or possible_nsubj.ent_type_ == "PER"):
                    verbs.append(possible_verb.text)
                    tmp_nsubj = possible_nsubj.text
                    foundNsubj = True
                    if possible_verb.text in nsubj:
                        nsubj[possible_verb.text].append(possible_nsubj.text)
                    else:
                        nsubj[possible_verb.text] = [possible_nsubj.text]

                    for possible_location in possible_verb.subtree:
                        for obj in possible_location.lefts:
                            if obj.ent_type_ == "GPE" or obj.ent_type_ == "FAC" or obj.ent_type_ == "LOC":
                                tmp_loc = obj.text
                                foundLocation = True
                                if possible_verb.text in loc:
                                    loc[possible_verb.text].append(obj.text)
                                else:
                                    loc[possible_verb.text] = [obj.text]
                        for obj in possible_location.rights:
                            if obj.ent_type_ == "GPE" or obj.ent_type_ == "FAC" or obj.ent_type_ == "LOC":
                                tmp_loc = obj.text
                                foundLocation = True
                                if possible_verb.text in loc:
                                    loc[possible_verb.text].append(obj.text)
                                else:
                                    loc[possible_verb.text] = [obj.text]

                    for possible_location in possible_verb.subtree:
                        for obj in possible_location.lefts:
                            if obj.ent_type_ == "GPE" or obj.ent_type_ == "FAC" or obj.ent_type_ == "LOC":
                                tmp_loc = obj.text
                                foundLocation = True
                                if possible_verb.text in loc:
                                    loc[possible_verb.text].append(obj.text)
                                else:
                                    loc[possible_verb.text] = [obj.text]
                        for obj in possible_location.rights:
                            if obj.ent_type_ == "GPE" or obj.ent_type_ == "FAC" or obj.ent_type_ == "LOC":
                                tmp_loc = obj.text
                                foundLocation = True
                                if possible_verb.text in loc:
                                    loc[possible_verb.text].append(obj.text)
                                else:
                                    loc[possible_verb.text] = [obj.text]

                    for possible_Date in possible_verb.subtree:
                        for obj in possible_Date.lefts:
                            if obj.ent_type_ == "DATE" or obj.text in months:
                                tmp_date = obj.text
                                foundDate = True
                                if possible_verb.text in date:
                                    date[possible_verb.text].append(obj.text)
                                else:
                                    date[possible_verb.text] = [obj.text]
                        for obj in possible_Date.rights:
                            if obj.ent_type_ == "DATE" or obj.text in months:
                                tmp_date = obj.text
                                foundDate = True
                                if possible_verb.text in date:
                                    date[possible_verb.text].append(obj.text)
                                else:
                                    date[possible_verb.text] = [obj.text]

        if foundDate and foundLocation and foundNsubj:
            for chunk in doc.noun_chunks:
                if tmp_nsubj in chunk.text:
                    tmp_nsubj = chunk.text
                if tmp_loc in chunk.text:
                    tmp_loc = chunk.text
                if tmp_date in chunk.text:
                    tmp_date = chunk.text

            argument_dict = \
            {
			    "template": "BORN",
			    "sentence": sentence,
			    "arguments":
                {
				    "1": tmp_nsubj,
				    "2": tmp_date,
				    "3": tmp_loc
			    }
		    }
            list_of_arguments.append(argument_dict)
            pp.pprint("Born({},{},{})".format(tmp_nsubj, tmp_loc, tmp_date), stream=outFile1)
            foundNsubj = False
            foundLocation = False
            foundDate = False
    #check for noun phrases/chunks --> check if word is head of noun chunk.
    for chunk in doc.noun_chunks:
        for key,value in nsubj.items():
            if chunk.root.text in value:
                value.remove(chunk.root.text)
                value.append(chunk.text)
        for key,value in loc.items():
            if chunk.root.text in value:
                value.remove(chunk.root.text)
                value.append(chunk.text)
        #print(chunk.text + "\t| " + chunk.root.text + "\t|" + chunk.root.dep_ + "\t|" + chunk.root.head.text)
    print(sentence)
    print(verbs)
    print(nsubj)
    print(date)
    print(loc)
    return list_of_arguments

#used for testing/demo purposes, does something similar to processFile1
def processFile2(output, output2, output3):
    p = init_pipe()
    files = scanFiles2("test_articles")
    for file in files:
        extraction = list()
        json_dict = dict()
        doc = feedToPipe(p, file)
        count = 0
        for tok in doc:
            print("Token:{}\nLemma:{}\nPOS:{}\nDep_parse:{}\n".format(tok.text, tok.lemma_, tok.pos_, tok.dep_))
            word, set = getSynsets(tok.text)
            # tup = (name, hypernyms, hyponyms, meronyms, holonyms)
            for s in set:
                print("Lemmas:")
                pp.pprint(s[0])
                print("Hypernymns:")
                pp.pprint(s[1])
                print("Hyponyms:")
                pp.pprint(s[2])
                print("Meronyms:")
                pp.pprint(s[3])
                print("Holonyms:")
                pp.pprint(s[4])
                print("********************************************************")

        for sent in doc.sents:
            print(sent.text)
            count +=1
            list1 = detectBuyRelation(p, sent.text, output)
            list2 = detectBornRelation(p, sent.text, output2)
            list3 = detectPartOfRelation(p, sent.text, output3)
            for entry in list1:
                extraction.append(entry)
            for entry in list2:
                extraction.append(entry)
            for entry in list3:
                extraction.append(entry)
            print("+++++++++++++++++++++++++++++++++" + str(count) + "++++++++++++++++++++++++++++++++++++")
        json_dict = \
        {
            "document": file.split("/")[1],
            "extraction": extraction

        }
        with open("json/"+file.split("/")[1].split(".")[0]+".json", 'w') as dumpFile:
            json.dump(json_dict, dumpFile, indent=5)

#process the files in a directory called articles2
def processFile1(output, output2, output3):
    p = init_pipe()
    files = scanFiles("articles2")
    for file in files:
        extraction = list()
        json_dict = dict()
        doc = feedToPipe(p, file)
        count = 0
        for sent in doc.sents:
            count +=1
            list1 = detectBuyRelation(p, sent.text, output)
            list2 = detectBornRelation(p, sent.text, output2)
            list3 = detectPartOfRelation(p, sent.text, output3)
            for entry in list1:
                extraction.append(entry)
            for entry in list2:
                extraction.append(entry)
            for entry in list3:
                extraction.append(entry)
            print("+++++++++++++++++++++++++++++++++" + str(count) + "++++++++++++++++++++++++++++++++++++")
        json_dict = \
        {
            "document": file.split("/")[1],
            "extraction": extraction

        }
        with open("json/"+file.split("/")[1].split(".")[0]+".json", 'w') as dumpFile:
            json.dump(json_dict, dumpFile, indent=5)

#scan file in directory and return list of file names
def scanFiles(dir):
    fileList = list()
    with os.scandir(dir) as files:
        for file in files:
            if file.is_file():
                fileList.append("articles2/" + file.name)
    return fileList

#scan file in directory and return list of file names
def scanFiles2(dir):
    fileList = list()
    with os.scandir(dir) as files:
        for file in files:
            if file.is_file():
                fileList.append("test_articles/" + file.name)
    return fileList

#p = init_pipe()
#doc = feedToPipe(p, test_doc)
#count = 0
#outFile1 = open("test_3.txt", 'w')
outFile_buy = open("buy.txt",'a')
outFile_born = open("born.txt",'a')
outFile_part = open("part.txt",'a')
processFile1(outFile_buy, outFile_born, outFile_part)
outFile_born.close()
outFile_part.close()
outFile_buy.close()
#processFile2(outFile1)
#outFile1.close()
#outFile1 = open("test_4.txt", 'w')
#detectBuyRelation(p, "NRG (Nederlandse Reassurantie Groep) – Berkshire acquired NRG, a Dutch life reinsurance company, from ING Group in December 2007.", outFile1)
#detectBornRelation(p, "Melinda Ann French was born on August 15, 1964 in Dallas, Texas.", outFile1)
# for sent in doc.sents:
#     count +=1
#     detectPartOfRelation(p, sent.text, outFile1)
#     print("+++++++++++++++++++++++++++++++++" + str(count) + "++++++++++++++++++++++++++++++++++++")
##outFile1.close()
# for token in doc:
#     print(token.text + "\t" + str(token.has_vector) + "\t" + str(token.vector_norm) + "\t" + str(token.is_oov) + "\t\n")

# count = 0
# for sent in doc.sents:
#     count +=1
#     print(sent)
#     print("+++++++++++++++++++" + str(count) + "+++++++++++++++++++++++")

# for tok in doc:
#     print(tok.text + "|" + tok.dep_ + "|" + tok.pos_ + "|" + tok.ent_type_ + "|\n")
#     print("*************************************************************")
# displacy.serve(doc, style="dep")

#dependancy parsing + entity recognitiion == good
#find verbs, find entities, dependency parsing (nsubj, nsubjpass)

# for chunk in doc.noun_chunks:
#     print(chunk.text + "\t| " + chunk.root.text + "\t|" + chunk.root.dep_ + "\t|" + chunk.root.head.text)

# word, set = getSynsets("born")
#
# for s in set:
#     pp.pprint(s[0])
#     pp.pprint(s[1])
#     pp.pprint(s[2])
#     pp.pprint(s[3])
#     pp.pprint(s[4])
#     print("********************************************************")

#hueristic(buy)
#   look for keywords (verb)
#   check for obj of verb and noun subj ---> head of nsubj should be keyword verb (noun chunks)
#   once keywords are detected look for entities (org, org, date)