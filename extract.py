#Final Project

import sys
import os


import sys
import pandas as pd
import numpy as np
import re
import pickle
import random
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import Perceptron
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

import mlModified
import mlDataProcessor

import math




#Input Processing
def main():

    featureList = ['WORD','WORD+1','WORD-1','ABBR', 'CAP', 'NUM','LOC','PREF','SUFF','PREP','NERTAG','NEXTWORDS','PREVWORDS'] #'LABEL+1','LABEL-1',

    trainingFileDirectory = r"development-anskeys"
    testFileDirectory = r"development-docs"
    #mlDataProcessor.main()

    #print("STARTING")
    #Read input files, use them to make a pathList and a fileList.
    filename = sys.argv[1]
    with open(filename) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    pathList = []
    fileList = []
    for line in lines:
        pathList.append(os.path.dirname(line) + "/")
        fileList.append(os.path.basename(line))

    #print(pathList)
    #print(fileList)
    
    featuresSet = set()
    for word in featureList:
        featuresSet.add(word)

    outputFilename = filename + ".templates"
    analyzeFileListOriginal(pathList, fileList,featuresSet,outputFilename)
    #print(pathList)
    #print(fileList)


def fullMLModelPipeline(contextRange,labelList,featuresSet,oCounterMax):
    processData(contextRange,labelList,oCounterMax)
    trainingFileName = "trainingData.csv"
    testFileName = "testData.csv"
    model, dictVectorizer = makeMLModel(trainingFileName,testFileName,featuresSet)
    
    return model,dictVectorizer

def processData(contextRange,labelList,oCounterMax):
    mlDataProcessor.main(contextRange,labelList,oCounterMax)

def makeMLModel(trainingCSV,testCSV,featuresSet):
    model, test_labels, vec_test_data, dictVectorizer = mlModified.createModel(trainingCSV,testCSV,featuresSet)
    return model, dictVectorizer


def analyzeFileList(pathList,fileList,featuresSet,docListName):
    print("Analyzing file list")

    fullLabelList = ['B-ACQUIRED','I-ACQUIRED','B-ACQBUS','I-ACQBUS','B-ACQLOC','I-ACQLOC','B-DLRAMT','I-DLRAMT','B-PURCHASER','I-PURCHASER','B-SELLER','I-SELLER','B-STATUS','I-STATUS','O']
    fullBasicLabelList = ['ACQUIRED','ACQLOC','ACQBUS','DLRAMT','PURCHASER','SELLER','STATUS','O']
    defaultOBalance = 100

    acquiredList = [3,math.inf,['B-ACQUIRED','I-ACQUIRED','O'],['ACQUIRED']]
    acqbusList = [3,defaultOBalance,['B-ACQBUS','I-ACQBUS','O'],['ACQBUS']]
    acqlocList = [3,defaultOBalance,['B-ACQLOC','I-ACQLOC','O'],['ACQLOC']]
    dlrAndStatusList = [3,math.inf,fullLabelList,['DLRAMT','STATUS']]
    purchaserList = [3,defaultOBalance,fullLabelList,['PURCHASER']]
    sellerList = [3,defaultOBalance,['B-SELLER','I-SELLER','O'],['SELLER']]
    tryEverythingList = [2,math.inf,fullLabelList,fullBasicLabelList]
    

    print("TRAINING MODELS")

    
    modelEVERYTHING, vectorizerEVERYTHING = fullMLModelPipeline(tryEverythingList[0],tryEverythingList[2],featuresSet,tryEverythingList[1])
    tryEverythingList.extend([modelEVERYTHING,vectorizerEVERYTHING])
    
    #modelACQUIRED, vectorizerACQUIRED = fullMLModelPipeline(acquiredList[0],acquiredList[2],featuresSet,acquiredList[1])
    #acquiredList.extend([modelACQUIRED,vectorizerACQUIRED])
    #print("1 model trained")

    modelACQBUS, vectorizerACQBUS = fullMLModelPipeline(acqbusList[0],acqbusList[2],featuresSet,acqbusList[1])
    acqbusList.extend([modelACQBUS,vectorizerACQBUS])
    print("2 models trained")
    
    modelACQLOC, vectorizerACQLOC = fullMLModelPipeline(acqlocList[0],acqlocList[2],featuresSet,acqlocList[1])
    acqlocList.extend([modelACQLOC,vectorizerACQLOC])
    print("3 models trained")

    modelDLRSTATUS, vectorizerDLRSTATUS = fullMLModelPipeline(dlrAndStatusList[0],dlrAndStatusList[2],featuresSet,dlrAndStatusList[1])
    dlrAndStatusList.extend([modelDLRSTATUS,vectorizerDLRSTATUS])
    print("4 models trained")

    modelPURCHASER, vectorizerPURCHASER = fullMLModelPipeline(purchaserList[0],purchaserList[1],featuresSet,purchaserList[1])
    purchaserList.extend([modelPURCHASER,vectorizerPURCHASER])
    print("5 models trained")


    modelSELLER, vectorizerSELLER = fullMLModelPipeline(sellerList[0],sellerList[2],featuresSet,sellerList[1])
    sellerList.extend([modelSELLER,vectorizerSELLER])
    print("6 models trained")

    
    
    
    
    
    


    
    #modelValsList = [acquiredList, acqbusList, acqlocList, dlrAndStatusList, purchaserList, sellerList]
    #modelValsList = [dlrAndStatusList]
    modelValsList = [tryEverythingList]
    #modelValsList = [sellerList]


    


    open(docListName, 'w').close() #This ensures we're writing to a blank file
    i = 0 
    while i < len(fileList):
        #print (os.path.isdir(pathList[i]))
        filePath = pathList[i] + fileList[i]
        #print (os.path.isfile(filePath))

        filePath = os.path.join(pathList[i], fileList[i])

        analyzeFile(filePath,featuresSet,docListName, modelValsList)
        i+=1


def analyzeFile(filePath, featuresSet,docListName, modelValsList):
    print("Analyzing file:" + filePath)

   

    tempFeatureList = ['LABEL','WORD','WORD+1','WORD-1','ABBR', 'CAP', 'NUM','LOC','PREF','SUFF','PREP','NERTAG','NEXTWORDS','PREVWORDS'] #'LABEL+1','LABEL-1'
    #tempFeatureList.insert(0,'LABEL')

    #print("Feature list" + str(tempFeatureList))

    finalClassifications = []

    def classifier(classifierContextRange,classifierLabelList,labelsToExtract, model, dictVectorizer,oCounterMax):
         #So, first we need a list of unlabeled words
        wordsList = mlDataProcessor.produceUntaggedWordList(filePath)

        #Then, we need to produce a vector list for those words
        unlabeledWordsData = mlDataProcessor.produceVectorList(wordsList, False, classifierContextRange, classifierLabelList,oCounterMax)
        mlDataProcessor.writeToCSV("temp.csv",tempFeatureList,unlabeledWordsData)
        test_df, test_labels = mlModified.read_csv_for_ml("temp.csv", list(featuresSet))
        
        

        #fileVectorList = mlFeatureExtractor.produceVectorList()
        wordsDataFrame = pd.DataFrame(unlabeledWordsData)
        #print(wordsData)
        #model, dictVectorizer = fullMLModelPipeline(classifierContextRange,classifierLabelList,featuresSet)
        
        
        

        
        vec_test_data = mlModified.vectorizeTestData(test_df,dictVectorizer)
        predictions = model.predict(vec_test_data) #Perform predictions with the model

        i = 0 
        wordPredictionPairs = []
        while i < len(predictions):
            wordPredictionPairs.append([predictions[i],wordsList[i][0]])
            i+=1

        classifications = []
        i = 0 
        slotEntry = ["",""]
        for word in wordPredictionPairs:
            predictedWordLabel = word[0]
            constructedSlotEntryLabel = slotEntry[0] #Label for the slot entry we're currently constructing
            predictedWordLabel = predictedWordLabel[2:] #Get the label, without the BI tag at the front
            predictedWord = word[1] #Get the word we made the prediction for

            if(predictedWordLabel == constructedSlotEntryLabel): #If the label for the current word matches the one for the slot entry we're constructing, we add the word to the entry.
                slotEntry.append(predictedWord)

            else: #Otherwise, we append the slot entry
                if(constructedSlotEntryLabel != ""):
                    if(predictedWordLabel in labelsToExtract): #We only append the entry if we're looking for entries with its label
                        classifications.append(slotEntry)
                slotEntry = [predictedWordLabel, predictedWord]
        #print(classifications)
        for classification in classifications:

            classificationString = classification[0]  + ": " #[2:] + ": "
            i = 1
            classificationPhraseString = ""
            while i < len(classification):
                classificationPhraseString = classificationPhraseString + " " + classification[i]
                i+=1

            classificationPhraseString = classificationPhraseString.lstrip()
            classificationPhraseString = classificationPhraseString.rstrip()
            classificationString += "\"" + classificationPhraseString + "\""

            finalClassifications.append(classificationString)
        print(finalClassifications)

    fullLabelList = ['B-ACQUIRED','I-ACQUIRED','B-ACQBUS','I-ACQBUS','B-ACQLOC','I-ACQLOC','B-DLRAMT','I-DLRAMT','B-PURCHASER','I-PURCHASER','B-SELLER','I-SELLER','B-STATUS','I-STATUS','O']

    #sellerList = [3,['B-SELLER','I-SELLER','O'],['SELLER'], model, vectorizer]
    for listItem in modelValsList:
        currentContextRange = listItem [0]
        currentCounterMax = listItem[1]
        currentLabelList = listItem[2]
        currentExtractionTargetsList = listItem[3]
        currentModel = listItem[4]
        currentVectorizer = listItem[5]
        

        classifier(currentContextRange,currentLabelList,currentExtractionTargetsList,currentModel,currentVectorizer,currentCounterMax)


    #VARIABLES FOR MODIFYING CLASSIFIER VARIABLES SHOULD GO IN THESE METHOD CALLS BELOW
    #classifier(3,['B-ACQUIRED','I-ACQUIRED','O'],['ACQUIRED']) #ACQUIRED
    #classifier(3,['B-ACQBUS','I-ACQBUS','O'],['ACQBUS']) #ACQBUS
    #classifier(3,['B-ACQLOC','I-ACQLOC','O'],['ACQLOC']) #ACQLOC
    #classifier(math.inf,fullLabelList,['DLRAMT','STATUS']) #DLRAMT and STATUS
    #classifier(7,fullLabelList,['PURCHASER']) #PURCHASER
    #classifier(3,['B-SELLER','I-SELLER','O'],['SELLER']) #SELLER
    #classifier(3,['B-STATUS','I-STATUS','O']) #STATUS
    #VARIABLES FOR MODIFYING CLASSIFIER VARIABLES SHOULD GO IN THESE METHOD CALLS ABOVE

    textTitle = "TEXT: " + os.path.basename(filePath)

    hasAcquired = False
    hasAcqbus = False
    hasAcqloc = False
    hasDlramt = False
    hasPurchaser = False
    hasSeller = False
    hasStatus = False
    for word in finalClassifications:
        
        if(word.startswith("ACQUIRED")):
            hasAcquired = True
        elif(word.startswith("ACQBUS")):
            hasAcqbus = True
        elif(word.startswith("ACQLOC")):
            hasAcqloc = True
        elif(word.startswith("DLRAMT")):
            hasDlramt = True
        elif(word.startswith("PURCHASER")):
            hasPurchaser = True
        elif(word.startswith("SELLER")):
            hasSeller = True
        elif(word.startswith("STATUS")):
            hasStatus = True

    emptyResult = "---"
    if not hasAcquired:
        finalClassifications.append("ACQUIRED: " + emptyResult)
    if not hasAcqbus:
        finalClassifications.append("ACQBUS: " + emptyResult)
    if not hasAcqloc:
        finalClassifications.append("ACQLOC: " + emptyResult)
    if not hasDlramt:
        finalClassifications.append("DLRAMT: " + emptyResult)
    if not hasPurchaser:
        finalClassifications.append("PURCHASER: " + emptyResult)
    if not hasSeller:
        finalClassifications.append("SELLER: " + emptyResult)
    if not hasStatus:
        finalClassifications.append("STATUS: " + emptyResult)
        
    finalClassifications.sort()

    print("FILE CLASSIFIED")

    with open(docListName, "a") as outputDoc:
        outputDoc.write(str(textTitle) + "\n")
        for classification in finalClassifications:
            outputDoc.write(classification + "\n")
        outputDoc.write("\n")



#This needs to be changed!!!
def analyzeFileOriginal(filePath, model,featuresSet, dictVectorizer,docListName,contextRange,labelList,counterMax):
    #filePath = r"C:\Users\bearl\Documents\Fall 2021\CS 5340\Final Project\5340Project\development-docs\369.txt" #"C:\\Users\\bearl\\Documents\\Fall 2021\\CS 5340\\Final Project\\5340Project\\development-docs\\369.txt'"
    print("Analyzing file: " + filePath)

    #So, first we need a list of unlabeled words

    wordsList = mlDataProcessor.produceUntaggedWordList(filePath)

    #Then, we need to produce a vector list for those words

    unlabeledWordsData = mlDataProcessor.produceVectorList(wordsList, False,contextRange,labelList,counterMax)
    #fileVectorList = mlFeatureExtractor.produceVectorList()

    wordsDataFrame = pd.DataFrame(unlabeledWordsData)
    #print(wordsData)

    tempFeatureList = ['LABEL','WORD','WORD+1','WORD-1','ABBR', 'CAP', 'NUM','LOC','PREF','SUFF','PREP','NERTAG','NEXTWORDS','PREVWORDS'] #'LABEL+1','LABEL-1'
    #tempFeatureList.insert(0,'LABEL')

    #print("Feature list" + str(tempFeatureList))
    mlDataProcessor.writeToCSV("temp.csv",tempFeatureList,unlabeledWordsData)

    test_df, test_labels = mlModified.read_csv_for_ml("temp.csv", list(featuresSet))


    vec_test_data = mlModified.vectorizeTestData(test_df,dictVectorizer)
    
    predictions = model.predict(vec_test_data) #Perform predictions with the model

    #print(predictions)

    i = 0 
    wordPredictionPairs = []
    while i < len(predictions):
        wordPredictionPairs.append([predictions[i],wordsList[i][0]])
        i+=1

    classifications = []
    i = 0 
    slotItem = ["",""]

    #Here, we build up 
    for word in wordPredictionPairs:
        wordLabel = word[0]
        slotLabel = slotItem[0]

        wordLabel = wordLabel[2:]
        #slotLabel = slotLabel[2:]
        if(wordLabel == slotLabel):
            slotItem.append(word[1])
        else:
            if(slotLabel != ""):
                classifications.append(slotItem) #If we get a new word, we take the one we've been building up and we throw it into the classifications list.
            slotItem = [wordLabel,word[1]]

    #print(classifications)

    finalClassifications = []
    textTitle = "TEXT: " + os.path.basename(filePath)

    for classification in classifications:

        classificationString = classification[0]  + ": " #[2:] + ": "
        i = 1
        classificationPhraseString = ""
        while i < len(classification):
            classificationPhraseString = classificationPhraseString + " " + classification[i]
            i+=1

        classificationPhraseString = classificationPhraseString.lstrip()
        classificationPhraseString = classificationPhraseString.rstrip()
        classificationString += "\"" + classificationPhraseString + "\""


        finalClassifications.append(classificationString)


    hasAcquired = False
    hasAcqbus = False
    hasAcqloc = False
    hasDlramt = False
    hasPurchaser = False
    hasSeller = False
    hasStatus = False
    for word in finalClassifications:
        
        if(word.startswith("ACQUIRED")):
            hasAcquired = True
        elif(word.startswith("ACQBUS")):
            hasAcqbus = True
        elif(word.startswith("ACQLOC")):
            hasAcqloc = True
        elif(word.startswith("DLRAMT")):
            hasDlramt = True
        elif(word.startswith("PURCHASER")):
            hasPurchaser = True
        elif(word.startswith("SELLER")):
            hasSeller = True
        elif(word.startswith("STATUS")):
            hasStatus = True

    emptyResult = "---"
    if not hasAcquired:
        finalClassifications.append("ACQUIRED: " + emptyResult)
    if not hasAcqbus:
        finalClassifications.append("ACQBUS: " + emptyResult)
    if not hasAcqloc:
        finalClassifications.append("ACQLOC: " + emptyResult)
    if not hasDlramt:
        finalClassifications.append("DLRAMT: " + emptyResult)
    if not hasPurchaser:
        finalClassifications.append("PURCHASER: " + emptyResult)
    if not hasSeller:
        finalClassifications.append("SELLER: " + emptyResult)
    if not hasStatus:
        finalClassifications.append("STATUS: " + emptyResult)
        
        

    finalClassifications.sort()

    #print(finalClassifications)

    with open(docListName, "a") as outputDoc:
        outputDoc.write(str(textTitle) + "\n")
        for classification in finalClassifications:
            outputDoc.write(classification + "\n")
        outputDoc.write("\n")

def analyzeFileListOriginal(pathList,fileList, featuresSet,docListName):
    print("Analyzing file list")


    fullLabelList = ['B-ACQUIRED','I-ACQUIRED','B-ACQBUS','I-ACQBUS','B-ACQLOC','I-ACQLOC','B-DLRAMT','I-DLRAMT','B-PURCHASER','I-PURCHASER','B-SELLER','I-SELLER','B-STATUS','I-STATUS','O']
    fullBasicLabelList = ['ACQUIRED','ACQLOC','ACQBUS','DLRAMT','PURCHASER','SELLER','STATUS','O']
    defaultOBalance = 100
    tryEverythingList = [2,math.inf,fullLabelList,fullBasicLabelList]
    

    print("TRAINING MODELS")

    
    modelEVERYTHING, vectorizerEVERYTHING = fullMLModelPipeline(tryEverythingList[0],tryEverythingList[2],featuresSet,tryEverythingList[1])

    open(docListName, 'w').close() #This ensures we're writing to a blank file
    i = 0 
    while i < len(fileList):
        #print (os.path.isdir(pathList[i]))
        filePath = pathList[i] + fileList[i]
        #print (os.path.isfile(filePath))

        filePath = os.path.join(pathList[i], fileList[i])

        analyzeFileOriginal(filePath, modelEVERYTHING, featuresSet, vectorizerEVERYTHING,docListName,tryEverythingList[0],tryEverythingList[2],tryEverythingList[1])
        i+=1

#def makeTemplates():


#TEXT: filename identifier
#ACQUIRED: entities that were acquired
#ACQBUS: the business focus of the acquired entities
#ACQLOC: the location of the acquired entities
#DLRAMT: the amount paid for the acquired entities
#PURCHASER: entities that purchased the acquired entities
#SELLER: entities that sold the acquired entities
#STATUS: status description of the acquisition event


#readInput()

if __name__ == '__main__':

    #trainingDirectory = sys.argv[1]
    main()