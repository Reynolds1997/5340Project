import spacy
import sys
import os
import entitySlotClassifier
import extractUtilities



#Our wrapper.
def main():
    print("Running Main")

    docListFile = sys.argv[2]
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

    rawTextString = open(filePath).read()
    print(rawTextString)
    #rawTextString = rawTextString.replace("\n", " ")
    #print(rawTextString)

    nerEntityList = spacyNER(rawTextString)

    slotItems = [["ACQUIRED"],["ACQBUS"],["ACQLOC"],["DLRAMT"],["PURCHASER"],["SELLER"],["STATUS"]]

    slotItems = entitySlotClassifier.classifyNEREntities(nerEntityList,rawTextString, slotItems)
    slotItems = classifyStatus(slotItems)

    textTemplate = formatSlots(slotItems, outputFile, fileTitle)


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


def classifyStatus(slotItems, rawText):
    print("Checking for STATUS slot candidates")
    statusesList = extractUtilities.fileToLineList("statuses.txt")

    rawText = rawText.lowerCase()
    for status in statusesList:
        if status in rawText:
            slotItems[6].append(status)

    
    #print(slotItems)
    return slotItems
    #Turn file into a lowercase string.
    #Remove punctuation. 

    #Check file for phrases
    #If a substring from statuses.txt appears in the text, use that substring.


def classifyDLDRAMT(slotItems):
    print("Checking for DLRAMT slot candidates...")

def formatSlots(slotItems, outputFile, textTitle):
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
        outputDoc.write(str(textTitle) + "\n")
        for templateLine in templateLines:
            outputDoc.write(templateLine + "\n")
        outputDoc.write("\n")
        #Write each line to output
    #Write a newline

    
    print(slotItems)

main()