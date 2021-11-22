


#Take in raw file 


from os import read, replace, write
import os
import sys
import csv
import re
from typing import final
import string
import spacy

def isAbbreviation(word):
    if(word[-1] == '.'):
        if(len(word) <= 4):
            
            testLine = word.replace('.','')
            if(testLine.isalpha()):
                return 1
    return 0

def isCap(word):
    if(word[0].isupper()):
        return 1
    else:
        return 0

def isPref(word):
    with open('prefixes.txt') as file:
        contents = file.read().splitlines() 
        
        if word in contents:
            return 1
        else:
            return 0

def isSuff(word):
    with open('suffixes.txt') as file:
        #contents = file.read()

        contents = file.read().splitlines() 
        #print(contents)
        if word in contents:
            #print(word)
            return 1
        else:
            return 0

def isPreposition(word):
    with open('prepositions.txt') as file:
        contents = file.read().splitlines() 
        
        if word in contents:
            return 1
        else:
            return 0

def isLoc(word):
    with open('locations.csv', 'r') as f:
        next(f)
        for line in f:

            line = line.replace(',', '')
            line = line.strip()
            line = line.split("\"")
            line = [x for x in line if x != '']

            #print(line)
            for entry in line:
                #print(entry + " vs " + word)
                if(entry.lower() == word.lower()):
                    return 1
        return 0

def isLocation(label):
    if label == "ACQLOC":
        return 1
    else:
        return 0

def containsNumber(word):
    for character in word:
        if character.isdigit():
            return 1
    return 0

def taggedListFromFiles(rawFile,goldFile):
    #These lists will contain the list of words and the list of labels
    docList = []
    goldList = []

    rawTextString = open(rawFile).read()

    rawTextString = rawTextString.replace("\n", " ")
    #print(rawTextString)

    processedTextString = rawTextString

    entityList = spacyNER(processedTextString)

    

    #processedTextString = processedTextString.translate(str.maketrans('', '', string.punctuation))

    goldLines = open(goldFile).readlines()
    goldLines = [line.rstrip() for line in goldLines]

    #print(goldLines)

    processedTextString2 = processedTextString


    entities = []
    basicEntityStrings = []
    basicEntityLabels = []
    for entity in entityList:
        phraseList = entity[0].split()
        entities.append([phraseList,entity[3]])

        basicEntityStrings.append(entity[0])
        basicEntityLabels.append(entity[3])



    finalLines = []
    for line in goldLines:
        if len(line) > 0:
            #print(line)
            lineList = line.split()
            #print(lineList)
            secondPhraseList = re.findall(r'"([^"]*)"', line)

            #print(secondPhraseList)

            if(len(secondPhraseList) >0):
                secondPhrase = secondPhraseList[0]
            else:
                secondPhrase = "---"
            firstPhrase = lineList[0]
            line = [firstPhrase,secondPhrase]
            #print(line)
            finalLines.append(line)

            if(len(secondPhraseList) > 1):
                nextPhrase = secondPhraseList[1]
                line = [firstPhrase,nextPhrase]
                #print(line)
                finalLines.append(line)
            #print(line)
            
            
    
    finalLines.remove(finalLines[0])

    #print(finalLines)

    for line in finalLines:
        stringToReplace = line[1]

        if stringToReplace in basicEntityStrings:
            nerTag = basicEntityLabels[basicEntityStrings.index(stringToReplace)]
        else:
            nerTag = "OTHER"

        #print(stringToReplace)
        replacementStringList = stringToReplace.split()

        
        replacementString = ""

        replacementStringList[0] += "^B-" + line[0][:-1]
        replacementString+= replacementStringList[0] + "^" + nerTag + " "
        i = 1
        while i < len(replacementStringList):
            replacementStringList[i] += "^I-" + line[0][:-1] + "^" + nerTag + " "

            replacementString+= replacementStringList[i]
            i+=1

    
            
        processedTextString = processedTextString.replace(stringToReplace,replacementString)

    #print(processedTextString)

    for entity in entityList:
        stringToReplace = entity[0]
        entityTag = entity[3]
        replacementString = stringToReplace+"^O^"+entityTag
        processedTextString.replace(stringToReplace,replacementString)

    textList = processedTextString.split()

    finalOutputList = []


    for word in textList:
        x = word.split("^")
        wordToBeAdded = []
        if len(x) > 2:
            wordToBeAdded = [x[0],x[1],x[2]]
        elif len(x) > 1:
            wordToBeAdded = [x[0],x[1],"OTHER"]
        else:
            wordToBeAdded = [x[0],"O","OTHER"]
        finalOutputList.append(wordToBeAdded)
        
    return finalOutputList
        
def produceUntaggedWordList(filePath):
    wordList = []

    outputList = []

    with open(filePath, "r") as f:
        wordList = f.read().split()

        for word in wordList:
            outputList.append([word,"0"])
    
    return outputList


#Given a directory of raw files and gold files, produces large lists of tagged words from each. 
def processFromDirectories(rawDirectory, goldDirectory, trainingDecimalPercent):
    rawFileList = os.listdir(rawDirectory)
    goldFileList = os.listdir(goldDirectory)

    fileCount = len(rawFileList)

    trainingCount = trainingDecimalPercent * fileCount

    i = 0

    #print("TEST")
        
    trainingWordList = []
    while i < trainingCount:
    #for filename in goldFileList:
        #print("TEST2")
        filename = goldFileList[i]
        rawFileName = filename[:-4]
        #print(rawFileName)
        rawFile = os.path.join(rawDirectory,rawFileName)
        goldFile = os.path.join(goldDirectory, filename)
        wordList = taggedListFromFiles(rawFile,goldFile)
        #print(wordList)
        #print("TEST3")
        for word in wordList:
            trainingWordList.append(word)
        #print("TEST3")
        i+=1
        
        
    #print("TEST")

    open('testPathList.txt', 'w').close() #Makes sure file is blank before writing
    testWordList = []
    while i < fileCount:
        filename = goldFileList[i]
        rawFileName = filename[:-4]
        #print(rawFileName)
        rawFile = os.path.join(rawDirectory,rawFileName)
        goldFile = os.path.join(goldDirectory, filename)
        wordList = taggedListFromFiles(rawFile,goldFile)
        #print(wordList)
        for word in wordList:
            testWordList.append(word)

        with open('testPathList.txt', 'a') as infile: #We create a doclist of paths for testing later
            infile.write(os.path.join(rawDirectory,filename[:-4]) + "\n")
        i+=1

    #print(i)

    #print(bigWordList)

    #print(len(bigWordList))

    return trainingWordList,testWordList

def produceVectorList(wordList,unlabeled):
    vectorList = []
    i = 0
    while i < len(wordList):
        
        wordVal = wordList[i][0] #The actual word
        #print(wordVal)
        if(len(wordVal) > 0):



            labelVal = wordList[i][1] #The word label
            if(len(wordList[i]) > 2):
                nerTagVal = wordList[i][2]
            else:
                nerTagVal = "OTHER"
        
            capVal = isCap(wordVal) #If the string starts with a capital
            abbrVal = isAbbreviation(wordVal)
            numVal = containsNumber(wordVal) #If the string contains a number
            locVal = isLoc(wordVal)
            prefVal = isPref(wordVal)
            prepVal = isPreposition(wordVal)
            suffVal = isSuff(wordVal)


            if i+1 < len(wordList):
                nextWord = wordList[i+1]
            else:
                nextWord = None
            if(nextWord != None  and len(nextWord[0]) > 0):# and len(nextWord[1]) > 0):
                wordPlusOne = nextWord[0]
                if(len(nextWord)) > 1:
                    labelPlusOne = nextWord[1]
                else:
                    labelPlusOne = "O"
                #posPlusOne = nextWord[1]
                suffVal = isSuff(nextWord[0])
            else:
                wordPlusOne = "OMEGA"
                labelPlusOne = "O"
                #posPlusOne = "OMEGAPOS"
                suffVal = 0

            if i-1 > 0:
                prevWord = wordList[i-1]
            else:
                prevWord = None
            if(prevWord != None and len(prevWord[0]) > 0):# and len(prevWord[1]) > 0):
                wordMinusOne = prevWord[0]
                if(len(prevWord)) > 1:
                    labelMinusOne = prevWord[1]
                else:
                    labelMinusOne = "O"
                #posMinusOne = prevWord[1]
                prefVal = isPref(prevWord[0])
            else:
                wordMinusOne = "PHI"
                labelMinusOne = "O"
                #posMinusOne = "PHIPOS"
                prefVal = 0
            #Idea: We should set it up to look at the words before and after. That could be a VERY useful feature for training.
            if unlabeled:
                labelVal = None

            if(labelVal == None):
                vector = [wordVal,wordPlusOne,wordMinusOne,abbrVal,capVal,numVal,locVal,prefVal,suffVal,prepVal,nerTagVal] #,labelPlusOne,labelMinusOne
            else:
                vector = [labelVal,wordVal,wordPlusOne,wordMinusOne,abbrVal,capVal,numVal,locVal,prefVal,suffVal,prepVal,nerTagVal] #,labelPlusOne,labelMinusOne
            vectorList.append(vector)

        i += 1
    
    return vectorList

def readFileIntoWordList(inputFile):

    wordList = []

    with open(inputFile, "r") as f:
        wordList = f.read().split()
    
    return wordList

def writeToCSV(fileName, fields, vectorList):
    with open(fileName, 'w') as csvfile:
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(vectorList)

def spacyNER(textString):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(textString)

    #for token in doc:
    #    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
    #            token.shape_, token.is_alpha, token.is_stop)
    entList = []
    for ent in doc.ents:
        entList.append([ent.text, ent.start_char, ent.end_char, ent.label_])

    return entList

def main():
    rawDirectory = r"development-docs"
    goldDirectory = r"development-anskeys"

    keyFile = r"development-anskeys\389.key"
    docFile = r"development-docs\389"

    #taggedListFromFiles(docFile,keyFile)
    
    trainingList, testList = processFromDirectories(rawDirectory,goldDirectory, 0.9)

    print("Processed from directories")

    trainingVectorList = produceVectorList(trainingList,False)
    testVectorList = produceVectorList(testList, False)

    print("Produced vector lists")
    #[labelVal,wordVal,wordPlusOne,wordMinusOne,labelPlusOne,labelMinusOne,abbrVal,capVal,numVal,locVal,prefVal,suffVal,prepVal]

    fields = ['LABEL','WORD','WORD+1','WORD-1','ABBR', 'CAP', 'NUM','LOC','PREF','SUFF','PREP','NERTAG'] #'LABEL+1','LABEL-1',
    #fields = ['LABEL','ABBR','CAP','LOC','POS','POS+1','POS-1','PREF','SUFF','WORD','WORD+1','WORD-1']
    writeToCSV("trainingData.csv", fields, trainingVectorList)
    writeToCSV("testData.csv", fields, testVectorList)


main()



    






    
        