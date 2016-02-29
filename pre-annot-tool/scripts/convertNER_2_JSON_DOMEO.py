#!/usr/bin/python
# -*- coding: utf-8 -*-

# convertSPL_NER_2_ODA.py
#
# Convert NER output to Open Data Annotation serialized in JSON and
# output a CSV file containing the preferred name, exact string, and
# URIs of all drug mentions
#
# Author: Richard Boyce, Andres Hernandez, Yifan Ning

# Copyright (C) 2012-2015 by Richard Boyce and the University of Pittsburgh
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json, sys, re
from os import walk
import xmltodict
import codecs
from sets import Set
import re
from bs4 import BeautifulSoup


############################################################
# Customizations

PREFIX_SUFFIX_SPAN = 60

inputNERDir = '../processed-output/'

inputProductLabelsDir = '../textfiles/'

############################################################
filesPddi = []

nerList = []
nerS = Set()

def regFixPrefixSuffix(text, mode):

    #soup = BeautifulSoup(text)
    #soup.prettify(formatter=lambda s: s.replace(u'\xa0', ' '))
    text = text.encode('utf-8').replace('\xa0',' ').replace('\xc2',' ')
    
    print "ORIGINAL TEXT - " + mode + "|" + text + "|"
    if mode is "prefix":
        regex = r'[^0-9A-Za-z\.\"\'\-\ \n\,\.\:\%\;\[\]\&]'
        iter = re.finditer(regex, text)
        indices = [m.end(0) for m in iter]
        if indices:
            #print indices
            end = indices[-1]
            print "PREFIX:" + text[end:]
            return text[end:]
        else:
            return text

    elif mode is "suffix":
        regex = r'[^0-9A-Za-z\.\"\'\-\ \n\,\.\:\%\;\[\]\&]'
        iter = re.finditer(regex, text)
        indices = [m.start(0) for m in iter]

        print re.findall(r"[^0-9A-Za-z\.\"\'\-\ \n\,\.\:\%\;\[\]\&]", text)

        print "INDICES: " + str(indices)

        if indices:
            start = indices[0]
            print "SUFFIX:" + text[:start]
            return text[:start]
        else:
            return text

    else:
        print "[WARNING:] regFixPrefixSuffix get wrong mode"
        return "ERROR"
        

# parse <annotationBean>
# Input annotBean in xml
# Output  Dict with attributes             
def parseAnnotationBean(drugMention, sectionText):

    drugName = drugMention['context']['term']['name']
    fromIdx = drugMention['context']['from']
    toIdx = drugMention['context']['to']

    drugURI = drugMention['concept']['fullId']

    print "[INFO:] find " + drugName + "|" + drugURI 

    preferredName = drugMention['concept']['preferredName']

    setId = re.sub(r'-[A-Za-z]+\.txt$', "", textFileName)

    if len(range(0,int(fromIdx))) < PREFIX_SUFFIX_SPAN:
        prefix = sectionText[0:int(fromIdx)-1]
    else:
        prefix = sectionText[int(fromIdx)-PREFIX_SUFFIX_SPAN:int(fromIdx)-1]

    prefix = regFixPrefixSuffix(prefix, "prefix")

    exact = sectionText[int(fromIdx)-1:int(toIdx)]

    if len(range(int(toIdx),len(sectionText))) < PREFIX_SUFFIX_SPAN:
        suffix = sectionText[int(toIdx):]
    else:
        suffix = sectionText[int(toIdx):int(toIdx)+PREFIX_SUFFIX_SPAN]

    suffix = regFixPrefixSuffix(suffix, "suffix")

    if "Added locally" in drugURI:
        print "[WARNING:] NER drug("+drugName+") URI is not available, drop from resultset"
        #print drugName + "|" + exact + "|" + unicode(textFileName) + "|" + prefix + "|"
        return None

    else:
        nerDict = {"setId":setId ,"name":drugName, "fullId":drugURI, "prefix":prefix,"exact":exact, "suffix":suffix, "from":fromIdx, "to":toIdx}
        return nerDict



## read all NER outputs in XML

for (dirpath, dirnames, filenames) in walk(inputNERDir):
    for fname in filenames:
        if fname.endswith("PROCESSED.xml") and (not fname.startswith("TABLE-")):
            filesPddi.append(fname)
    break


for ner in filesPddi:
    with codecs.open(inputNERDir + ner, 'r', 'utf-8') as jsonInputFile:
        
        textFileName = ner.strip('-PROCESSED.xml')

        with codecs.open(inputProductLabelsDir + textFileName, 'r', 'utf-8') as textInputFile:
            sectionText = textInputFile.read()
            print "[INFO:]" + textFileName
            
            jsonResult = xmltodict.parse(jsonInputFile.read())

            drugL = []
            if jsonResult['root']['data']['annotatorResultBean']['annotations']:
                drugL = jsonResult['root']['data']['annotatorResultBean']['annotations']['annotationBean']
            else:
                print "[DEBUG:] not annotations in XML"
                continue

            if isinstance(drugL, list):
            
                for drugMention in drugL:
                    nerDict = parseAnnotationBean(drugMention, sectionText)
                    if nerDict:
                        nerKey = nerDict["setId"] + "-" + nerDict["from"] + "-" + nerDict["to"]
                        if nerKey not in nerS:
                            nerList.append(nerDict)
                            nerS.add(nerKey)
                            print "%s, %s|%s|%s|%s|" % (nerDict["setId"],nerDict["name"], nerDict["prefix"], nerDict["exact"], nerDict["suffix"])

            ## only one NER (not a list)                
            else:
                print "[INFO:] Single NER"
                drugMention = jsonResult['root']['data']['annotatorResultBean']['annotations']['annotationBean']
                nerDict = parseAnnotationBean(drugMention, sectionText)
                if nerDict:
                    nerKey = nerDict["setId"] + "-" + nerDict["from"] + "-" + nerDict["to"]
                    if nerKey not in nerS:
                        nerList.append(nerDict)
                        nerS.add(nerKey)
                        print "Single NER %s, %s|%s|%s|%s|" % (nerDict["setId"],nerDict["name"], nerDict["prefix"], nerDict["exact"], nerDict["suffix"])

                
with codecs.open('NER-outputs.json', 'w', 'utf-8') as nerOutput:
    json.dump(nerList, nerOutput)
            

with open('NER-output.csv','w') as nerOutput:
    for element in nerList:
        line = str(element['setId'])+';'+str(element['name'])+';'+str(element['exact'])+';'+str(element['fullId'])
        print >>  nerOutput, line



