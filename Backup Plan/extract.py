import math
import spacy
import sys
import os
import extractUtilities
import re

# maximum amount of "words" a phrase can be away from a "transaction" word before it no longer counts
## only applies to the first word in an NP
maxTransactionWordDistance = 15

# applies if the word "acquired" is found anywhere, any phrases within this window that can be "acquired" are tagged as such
maxAcquiredDistance = 10

#Our wrapper.
def main():
    print("Running Main")

    docListFile = sys.argv[1]
    docListFileName = os.path.basename(docListFile)

    #Read in the document list from the file, to get the paths to the files we want to analyze
    docPathsList = []


    docPathsList = extractUtilities.fileToLineList(docListFile)

    #with open(docListFile, "r") as docList:
    #    docPathList = docList.readlines()

    path = sys.path[0]
    path = os.path.join(path,"447")

    #Create the templates file
    outputFile = docListFileName + ".templates" 
    open(outputFile, 'w').close()#Make sure the output file is blank before writing

    #Analyze the files in the list
    analyzeFiles(docPathsList,outputFile)

    #analyzeFile(path, outputFile)

#Analyze a list of files
def analyzeFiles(filePaths, outputFile):
    for filePath in filePaths:
        analyzeFile(filePath, outputFile)

#Analyze a single file
def analyzeFile(filePath, outputFile):
    print("Analyzing file: " + str(filePath))

    fileTitle = os.path.basename(filePath)

    if filePath[-1] == "\n":
        rawTextString = open(filePath[:-1]).read()
    else:
        rawTextString = open(filePath).read()
    #print(rawTextString)
    #rawTextString = rawTextString.replace("\n", " ")
    #print(rawTextString)

    nerEntityList = spacyNER(rawTextString)

    slotItems = [["ACQUIRED"],["ACQBUS"],["ACQLOC"],["DLRAMT"],["PURCHASER"],["SELLER"],["STATUS"]]

    definitiveCount = 0
    defininiveWord = ""
    acquiredExists = False
    acquiredCount = 0

    # finds the "transaction" word in a document
    ## if no such word exists then it's assumed the "seller" and "buyer" don't exist
    ## also remembers the position of the word for later
    for entity in nerEntityList:
        entityWord = entity[0].lower()
        if entityWord == "sell" or entityWord == "buy" :
            defininiveWord = entityWord
            break
        definitiveCount = definitiveCount + 1

    for entity in nerEntityList:
        entityWord = entity[0].lower()
        if entityWord == "acquired" :
            acquiredExists = True
            break
        acquiredCount = acquiredCount + 1

    
    # dictionaries in Python are pass by reference, so no need to set it on each method
    classifyACQBUS(slotItems,rawTextString)
    classifySTATUS(slotItems,rawTextString)
    classifyDLRAMT(slotItems,rawTextString)

    # deleted references to entitySlotClassifier cause i really wanted to separate these into their own functions
    classifyACQUIRED(slotItems,rawTextString,nerEntityList,acquiredExists,acquiredCount)
    classifyACQLOC(slotItems,rawTextString,nerEntityList)
    classifyPURCHASER(slotItems,rawTextString,nerEntityList,defininiveWord,definitiveCount)
    classifySELLER(slotItems,rawTextString,nerEntityList,defininiveWord,definitiveCount)

    formatSlots(slotItems, outputFile, fileTitle)


def spacyNER(textString):
    #print(textString)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(textString)
    #print(doc.ents)

    #for token in doc:
    #    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
    #            token.shape_, token.is_alpha, token.is_stop)
    entList = []
    for ent in doc.ents:
        entList.append([ent.text, ent.label_])

    return entList

def classifyACQBUS(slotItems, rawText):
    #print("Checking for ACQBUS slot candidates")
    acqbusesList = extractUtilities.fileToLineList("acqbuses.txt")
    acqbusCandidatesList = []
    rawText = rawText.lower()
    rawText = rawText.replace(".","")
    rawText = rawText.replace("\n"," ")

    for acqbus in acqbusesList:
        if acqbus in rawText:
            acqbusCandidatesList.append(acqbus)


    if len(acqbusCandidatesList) > 0:
        bestCandidate = ""
        for acqbus in acqbusCandidatesList:
            candidateList = bestCandidate.split()
            currCandidateLen = len(candidateList)
            acqbusList = acqbus.split()           
            acqbusListLen = len(acqbusList)

            if (acqbusListLen > currCandidateLen): #Picks the longest phrase that came from the dictionary.
                bestCandidate = acqbus
            elif(acqbusListLen == currCandidateLen): #As a tie breaker, picks the phrase that shows up in the dictionary the most.
                if(acqbusList.count(acqbus) > acqbusList.count(bestCandidate)):
                    bestCandidate = acqbus


        
        slotItems[1].append(bestCandidate)

    
    #print(slotItems)
    return
    #Check file for phrases
    #If a substring from statuses.txt appears in the text, use that substring.

def classifySTATUS(slotItems, rawText):
    #print("Checking for STATUS slot candidates")
    statusesList = extractUtilities.fileToLineList("statuses.txt")
    statusCandidatesList = []
    rawText = rawText.lower()
    rawText = rawText.replace(".","")
    rawText = rawText.replace("\n"," ")
    
    
    for status in statusesList:
        if status in rawText:
            statusCandidatesList.append(status)

    if len(statusCandidatesList) > 0:
        bestCandidate = ""
        for status in statusCandidatesList:
            candidateList = bestCandidate.split()
            currCandidateLen = len(candidateList)
            statusList = status.split()           
            statusListLen = len(statusList)

            if (statusListLen > currCandidateLen): #Picks the longest phrase that came from the dictionary.
                bestCandidate = status
            elif(statusListLen == currCandidateLen): #As a tie breaker, picks the phrase that shows up in the dictionary the most.
                if(statusesList.count(status) > statusList.count(bestCandidate)):
                    bestCandidate = status

        slotItems[6].append(bestCandidate)
        
       



    #print(slotItems)
    #Turn file into a lowercase string.
    #Remove punctuation. 
    return
    #Check file for phrases
    #If a substring from statuses.txt appears in the text, use that substring.


def classifyDLRAMT(slotItems, rawText):
    #print("Checking for DLRAMT slot candidates...")

    moneyClues, secondaryMoneyClues = extractUtilities.dlramtHelper()
    #print(moneyClues)

    #rawText = rawText.replace(".","")
    rawText = rawText.replace("\n"," ")
    #print(rawText)

    rawTextList = rawText.split()
        
    for clue in moneyClues:
        clueWordList = clue.split()

        if(clue in rawText):
            clueBase = clue
            indexes = extractUtilities.returnIndexes(rawTextList,clueWordList[0])
            for index in indexes:
                finalClue = rawTextList[index-1] + " " + clueBase
                slotItems[3].append(finalClue)


    for clue in secondaryMoneyClues:
        if(clue in rawText):
            slotItems[3].append(clue)

    return

def classifyACQUIRED(slotItems,rawText,nerEntityList,acquiredExists,acquiredCount) :

    chainString = ""
    currLabel = "NONE"
    mainCount = 0

    for entity in nerEntityList:
        entityWord = entity[0]
        entityLabel = entity[1]

        currDistance = math.fabs(mainCount - acquiredCount)
        withinRange = currDistance <= maxTransactionWordDistance


        if entityLabel != currLabel and chainString != "" :
            slotItems[0].append(chainString)
            chainString = ""

        if entityLabel == "ORG" or entityLabel == "FAC" :
            if (acquiredExists and mainCount < acquiredCount and withinRange) or chainString != "" :
                if chainString == "" :
                    chainString = entityWord
                else :
                    chainString = chainString + " " + entityWord
        
        mainCount = mainCount + 1
    
    return

def classifyACQLOC(slotItems,rawText,nerEntityList) :

    chainString = ""
    currLabel = "NONE"

    for entity in nerEntityList:
        entityWord = entity[0]
        entityLabel = entity[1]

        if entityLabel != currLabel and chainString != "" :
            slotItems[2].append(chainString)
            chainString = ""

        if entityLabel == "GPE" or entityLabel == "FAC" :
            if chainString == "" :
                chainString = entityWord
            else :
                chainString = chainString + " " + entityWord

    return

def classifyPURCHASER(slotItems,rawText,nerEntityList,defininiveWord,definitiveCount) :
    chainString = ""
    currLabel = "NONE"
    mainCount = 0

    for entity in nerEntityList:
        entityWord = entity[0]
        entityLabel = entity[1]

        currDistance = math.fabs(mainCount - definitiveCount)
        withinRange = currDistance <= maxTransactionWordDistance


        if entityLabel != currLabel and chainString != "" :
            slotItems[4].append(chainString)
            chainString = ""

        if entityLabel == "ORG" :
            if (defininiveWord == "sell" and mainCount > definitiveCount and withinRange) or (defininiveWord == "buy" and mainCount < definitiveCount and withinRange) or chainString != "" :
                if chainString == "" :
                    chainString = entityWord
                else :
                    chainString = chainString + " " + entityWord
        
        mainCount = mainCount + 1

    return

def classifySELLER(slotItems,rawText,nerEntityList,defininiveWord,definitiveCount) :
    chainString = ""
    currLabel = "NONE"
    mainCount = 0

    for entity in nerEntityList:
        entityWord = entity[0]
        entityLabel = entity[1]

        currDistance = math.fabs(mainCount - definitiveCount)
        withinRange = currDistance <= maxTransactionWordDistance


        if entityLabel != currLabel and chainString != "" :
            slotItems[5].append(chainString)
            chainString = ""

        if entityLabel == "ORG" :
            if (defininiveWord == "sell" and mainCount < definitiveCount and withinRange) or (defininiveWord == "buy" and mainCount > definitiveCount and withinRange) or chainString != "" :
                if chainString == "" :
                    chainString = entityWord
                else :
                    chainString = chainString + " " + entityWord
        
        mainCount = mainCount + 1

    return


def formatSlots(slotItems, outputFile, textTitle):
    #print("Writing to file now")
    templateLines = []
    for slot in slotItems:
        currentLabel = slot[0]
        slotVals = slot[1:] #Every val but the first
        if len(slot) == 1:
            templateLines.append(currentLabel + ": ---") 
        else:
            for slotVal in slotVals:
                templateLines.append(currentLabel + ": " + "\"" + slotVal + "\"")

    #Write text title line to output
    
    with open(outputFile, "a") as outputDoc:
        outputDoc.write("TEXT: " + str(textTitle) + "\n")
        for templateLine in templateLines:
            outputDoc.write(templateLine + "\n")
        outputDoc.write("\n")
        #Write each line to output
    #Write a newline

    
    #print(slotItems)

main()