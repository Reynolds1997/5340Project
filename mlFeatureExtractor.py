from os import read
import sys
import csv


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


def produceVectorList(wordsList):
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
    while i < len(wordsList):
        
        wordEntry = wordsList[i]

        if(len(wordEntry) > 0):
            #print(wordEntry)
            labelVal = wordEntry[0]
            posVal = wordEntry[1]
            wordVal = wordEntry[2]
            abbrVal = isAbbreviation(wordVal)
            capVal = isCap(wordVal)

            nextWord = wordsList[i+1]
            if(len(nextWord) >0):
                wordPlusOne = nextWord[2]
                posPlusOne = nextWord[1]
                suffVal = isSuff(nextWord[2])
            else:
                wordPlusOne = "OMEGA"
                posPlusOne = "OMEGAPOS"
                suffVal = 0

            prevWord = wordsList[i-1]
            if(len(prevWord) >0):
                wordMinusOne = prevWord[2]
                posMinusOne = prevWord[1]
                prefVal = isPref(prevWord[2])
            else:
                wordMinusOne = "PHI"
                posMinusOne = "PHIPOS"
                prefVal = 0

            locVal = isLoc(wordVal)
            
            vector = [labelVal,abbrVal,capVal,locVal,posVal,posPlusOne,posMinusOne,prefVal,suffVal,wordVal,wordPlusOne,wordMinusOne]
            vectorList.append(vector)

        i += 1
    
    return vectorList





def readFile(inputFile):

    lines = inputFile.readlines()
    lines = [line.rstrip() for line in lines]
    lines = [line.split() for line in lines]

    blank = []
    lines.insert(0,blank)

    return lines

def writeToCSV(fileName, fields, vectorList):
    with open(fileName, 'w') as csvfile:
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(vectorList)

def main():

    trainingSentencesList  = []
    testSentencesList = []
    testSentencesStringList = []

    #Read the training file
    with open(sys.argv[1], 'r') as trainingFile:
        trainingFileList = readFile(trainingFile)


    #Read the test file    
    with open(sys.argv[2], 'r') as testFile:

        testFileList = readFile(testFile)

    trainingFileVectorList = produceVectorList(trainingFileList)
    testFileVectorList = produceVectorList(testFileList)

    #print(trainingFileVectorList)
    #print(testFileVectorList)
    #print(testSentencesList)
    #print(trainingSentencesList)

    fields = ['LABEL','ABBR','CAP','LOC','POS','POS+1','POS-1','PREF','SUFF','WORD','WORD+1','WORD-1']

    trainingFileName = sys.argv[1].rsplit('.',1)[0] + '_ft.csv'
    testFileName = sys.argv[2].rsplit('.',1)[0] + '_ft.csv'

    writeToCSV(trainingFileName,fields,trainingFileVectorList)
    writeToCSV(testFileName,fields,testFileVectorList)
    
main()