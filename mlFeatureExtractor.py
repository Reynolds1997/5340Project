from os import read, write
import os
import sys
import csv
import re

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

def produceVectorList(linesList):
   #CHECK #WORD: the word w itself. 
   #CHECK #POS: the POS tag p of w.
   #CHECK #ABBR: a binary feature indicating whether w is an abbreviation. An abbreviation must: (1) end with a period, (2) consist entirely of alphabetic characters [a-z][A-Z] and one or more periods (including the ending one), and (3) have length ≤4.
   #CHECK #CAP: a binary feature indicating whether the first letter of w is capitalized.
    #WORD+1: the word w+1 that immediately follows w in the sentence.
    #WORD-1: the word w−1 that immediately precedes w in the sentence.
    #POS+1: the POS tag p+1 of the word that immediately follows w in the sentence.
    #POS-1: the POS tag p−1 of the word that immediately precedes w in the sentence.
    #LOC: a binary feature indicating whether w matches any of the countries or capital cities listed in the provided file locations.csv. Please do case-insensitive matching against this file (e.g., “Israel” should match “ISRAEL”).
    #PREF: a binary feature indicating whether the word w−1 that immediately precedes w matches any of the prefix terms listed in the provided file prefixes.txt.
    #SUFF: a binary feature indicating whether the word w+1 that immediately follows w matches any of the suffix terms listed in the provided file suffixes.txt.

    vectorList = []
    i = 0
    while i < len(linesList):
        
        wordEntry = linesList[i]

        if(len(wordEntry) > 0):
            #print(wordEntry)

            #Here is where we call the methods that create features.
            
            basicLabelVal = wordEntry[0]

            basicLabelVal = basicLabelVal.replace(":","") #Strip off colon
            
            basicWordVal = wordEntry[1]
            basicWordVal = basicWordVal.replace("\"","") #Strip off quotation marks from beginning and end
            
            if basicLabelVal != "TEXT" and basicWordVal != "---": 

                wordList = basicWordVal.split()

                j = 0 

                #print(len(wordList))
                #print(wordList)
                while j < len(wordList):
                    
                    #Here we do some IOB tagging
                    if(j == 0):
                        labelVal= "B-" + basicLabelVal
                    else:
                        labelVal = "I-" + basicLabelVal

                    wordVal = wordList[j]
                    capVal = isCap(wordVal) #If the string starts with a capital
                    numberVal = containsNumber(wordVal) #If the string contains a number
                    locationVal = isLocation(basicLabelVal)
                    prefixVal = isPref(wordVal)
                    prepVal = isPreposition(wordVal)
                    suffixVal = isSuff(wordVal)

                    #Idea: We should set it up to look at the words before and after. That could be a VERY useful feature for training.

                    vector = [labelVal,wordVal,capVal,numberVal,locationVal,prefixVal,prepVal,suffixVal] #abbrVal,capVal,locVal,posVal,posPlusOne,posMinusOne,prefVal,suffVal,wordVal,wordPlusOne,wordMinusOne]
                    vectorList.append(vector)

                    j+=1

           # posVal = wordEntry[1]
           # 
           # abbrVal = isAbbreviation(wordVal)
           # capVal = isCap(wordVal)

            # https://stackoverflow.com/questions/6173118/shortcut-to-comment-out-multiple-lines-with-python-tools-for-visual-studio
            # nextWord = wordsList[i+1]
            # if(len(nextWord) >0):
            #     wordPlusOne = nextWord[2]
            #     posPlusOne = nextWord[1]
            #     suffVal = isSuff(nextWord[2])
            # else:
            #     wordPlusOne = "OMEGA"
            #     posPlusOne = "OMEGAPOS"
            #     suffVal = 0

            # prevWord = wordsList[i-1]
            # if(len(prevWord) >0):
            #     wordMinusOne = prevWord[2]
            #     posMinusOne = prevWord[1]
            #     prefVal = isPref(prevWord[2])
            # else:
            #     wordMinusOne = "PHI"
            #     posMinusOne = "PHIPOS"
            #     prefVal = 0

            #locVal = isLoc(wordVal)
            
            

        i += 1
    
    return vectorList


#What we do here is we take every doc in a directory, turn a ratio of them into training data, and then another set of them into test data.
def produceTestAndTrainingFiles(goldDirectory,rawDirectory,trainingDecimalPercent):

    fileList = os.listdir(goldDirectory)

    #print(fileList)

    fileCount = len(fileList)

    trainingCount = trainingDecimalPercent * fileCount

    i = 0

    with open('trainingFile.txt', 'w') as outfile:
        while i < trainingCount:
            with open(goldDirectory + "/" + fileList[i]) as infile:
                for line in infile:
                    outfile.write(line)
            i+=1
    
    
    open('testPathList.txt', 'w').close() #Makes sure file is blank before writing
    with open('testFile.txt', 'w') as outfile:
        while i < fileCount:
            with open(goldDirectory + "/" + fileList[i]) as infile:
                for line in infile:
                    outfile.write(line)

            with open('testPathList.txt', 'a') as infile:

                inputFile = fileList[i]

                size = len(inputFile)
                # Slice string to remove last character from string
                mod_string = inputFile[:size - 4]

                infile.write(rawDirectory + "/" + mod_string + "\n")



            i+=1

    


def produceUnlabeledVectorsFromWordList(inputWordList):
    vectorList = []
    i = 0
    while i < len(inputWordList):
        
        wordEntry = inputWordList[i]

        if(len(wordEntry) > 0):
            #print(wordEntry)

            #Here is where we call the methods that create features.
            
            basicLabelVal = 0

            #basicLabelVal = basicLabelVal.replace(":","") #Strip off colon
            
            basicWordVal = wordEntry
            basicWordVal = basicWordVal.replace("\"","") #Strip off quotation marks from beginning and end
            
            if basicLabelVal != "TEXT" and basicWordVal != "---": 

                wordList = basicWordVal.split()

               

                basicLabelVal = 0
                wordVal = basicWordVal
                capVal = isCap(wordVal) #If the string starts with a capital
                numberVal = containsNumber(wordVal) #If the string contains a number

                locationVal = isLocation(basicLabelVal)
                prefixVal = isPref(wordVal)
                prepVal = isPreposition(wordVal)
                suffixVal = isSuff(wordVal)

                    #Idea: We should set it up to look at the words before and after. That could be a VERY useful feature for training.

                vector = [basicLabelVal,wordVal,capVal,numberVal, locationVal,prefixVal,prepVal,suffixVal] #abbrVal,capVal,locVal,posVal,posPlusOne,posMinusOne,prefVal,suffVal,wordVal,wordPlusOne,wordMinusOne]
                vectorList.append(vector)

        i+= 1
    return vectorList

def readFileIntoWordList(inputFile):

    wordList = []

    with open(inputFile, "r") as f:
        wordList = f.read().split()
    
    return wordList



def readFileIntoLineList(inputFile):

    initialLines = inputFile.readlines()
    initialLines = [line.rstrip() for line in initialLines]

    finalLines = []
    for line in initialLines:
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

    #print(finalLines)

    blank = []
    finalLines.insert(0,blank)

    return finalLines

def writeToCSV(fileName, fields, vectorList):
    with open(fileName, 'w') as csvfile:
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(vectorList)

def main(inputFileDirectory,rawFileDirectory):

    trainingSentencesList  = []
    testSentencesList = []
    testSentencesStringList = []

    #inputFileDirectory = "C:\\Users\\bearl\\Documents\\Fall 2021\\CS 5340\\Final Project\\5340Project\\development-anskeys"

    #inputFileDirectory
    trainingPercentageDecimal = 0.9
    produceTestAndTrainingFiles(inputFileDirectory,rawFileDirectory,trainingPercentageDecimal)

    # #Read the training file
    # with open(sys.argv[1], 'r') as trainingFile:
    #     trainingFileList = readFile(trainingFile)

    # #Read the test file    
    # with open(sys.argv[2], 'r') as testFile:
    #     testFileList = readFile(testFile)

    with open('trainingFile.txt','r') as trainingFile:
        trainingFileLinesList = readFileIntoLineList(trainingFile)
    with open('testFile.txt','r') as testFile:
        testFileLinesList = readFileIntoLineList(testFile)

    trainingFileVectorList = produceVectorList(trainingFileLinesList)
    testFileVectorList = produceVectorList(testFileLinesList)

    #print(trainingFileVectorList)
    #print(testFileVectorList)
    #print(testSentencesList)
    #print(trainingSentencesList)

    fields = ['LABEL','WORD','CAP','NUM','LOC','PREF','PREP','SUFF']
    #fields = ['LABEL','ABBR','CAP','LOC','POS','POS+1','POS-1','PREF','SUFF','WORD','WORD+1','WORD-1']

   # trainingFileName = sys.argv[1].rsplit('.',1)[0] + '_ft.csv'
   # testFileName = sys.argv[2].rsplit('.',1)[0] + '_ft.csv'


    trainingFileName = "trainingFt.csv"
    testFileName = "testFt.csv"
    writeToCSV(trainingFileName,fields,trainingFileVectorList)
    writeToCSV(testFileName,fields,testFileVectorList)
    
if __name__ == '__main__':

    trainingDirectory = sys.argv[1]
    main(trainingDirectory)