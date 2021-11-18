


#Take in raw file 


from os import read, replace, write
import os
import sys
import csv
import re
from typing import final



def updateNER(rawFile,goldFile):
    #These lists will contain the list of words and the list of labels
    docList = []
    goldList = []

    rawTextString = open(rawFile).read()
    #print(rawTextString)

    processedTextString = rawTextString

    goldLines = open(goldFile).readlines()
    goldLines = [line.rstrip() for line in goldLines]

    #print(goldLines)

    finalLines = []
    for line in goldLines:
        if len(line) > 0:
            #print(line)
            lineList = line.split()
            #print(lineList)
            secondPhraseList = re.findall(r'"([^"]*)"', line)

            if(len(secondPhraseList) >0):
                secondPhrase = secondPhraseList[0]
            else:
                secondPhrase = "---"
            firstPhrase = lineList[0]
            line = [firstPhrase,secondPhrase]
            #print(line)
            finalLines.append(line)
    
    finalLines.remove(finalLines[0])

    #print(finalLines)

    for line in finalLines:
        stringToReplace = line[1]
        replacementStringList = stringToReplace.split()

        
        replacementString = ""

        replacementStringList[0] += "-B-" + line[0]
        replacementString+= replacementStringList[0] + " "
        i = 1
        while i < len(replacementStringList):
            replacementStringList[i] += "-I-" + line[0] + " "

            replacementString+= replacementStringList[i]
            i+=1

    
            
        processedTextString = processedTextString.replace(stringToReplace,replacementString)

    print(processedTextString)
        



keyFile = r"development-anskeys\389.key"
docFile = r"development-docs\389"
print("HELLO WORLD")
updateNER(docFile,keyFile)

    
        
