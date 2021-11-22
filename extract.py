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
import mlFeatureExtractor
import mlDataProcessor



#Input Processing
def main():

    featureList = ['WORD','WORD+1','WORD-1','ABBR', 'CAP', 'NUM','LOC','PREF','SUFF','PREP','NERTAG'] #'LABEL+1','LABEL-1',

    trainingFileDirectory = r"development-anskeys"
    testFileDirectory = r"development-docs"
    mlDataProcessor.main()

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

    trainingFileName = "trainingData.csv"
    testFileName = "testData.csv"
    featuresSet = set()

    outputFilename = filename + ".templates"
    for word in featureList:
        featuresSet.add(word)
    model, dictVectorizer = makeMLModel(trainingFileName,testFileName,featuresSet)
    analyzeFileList(pathList, fileList, model,featuresSet, dictVectorizer,outputFilename)
    #print(pathList)
    #print(fileList)



def makeMLModel(trainingCSV,testCSV,featuresSet):
    model, test_labels, vec_test_data, dictVectorizer = mlModified.createModel(trainingCSV,testCSV,featuresSet)
    return model, dictVectorizer

def analyzeFileList(pathList,fileList, model,featuresSet, dictVectorizer,docListName):
    print("Analyzing file list")

    open(docListName, 'w').close() #This ensures we're writing to a blank file
    i = 0 
    while i < len(fileList):
        #print (os.path.isdir(pathList[i]))
        filePath = pathList[i] + fileList[i]
        #print (os.path.isfile(filePath))

        filePath = os.path.join(pathList[i], fileList[i])

        analyzeFile(filePath, model, featuresSet, dictVectorizer,docListName)
        i+=1





#This needs to be changed!!!
def analyzeFile(filePath, model,featuresSet, dictVectorizer,docListName):
    #filePath = r"C:\Users\bearl\Documents\Fall 2021\CS 5340\Final Project\5340Project\development-docs\369.txt" #"C:\\Users\\bearl\\Documents\\Fall 2021\\CS 5340\\Final Project\\5340Project\\development-docs\\369.txt'"
    print("Analyzing file: " + filePath)

    #So, first we need a list of unlabeled words

    wordsList = mlDataProcessor.produceUntaggedWordList(filePath)

    #Then, we need to produce a vector list for those words

    unlabeledWordsData = mlDataProcessor.produceVectorList(wordsList, False)
    #fileVectorList = mlFeatureExtractor.produceVectorList()

    wordsDataFrame = pd.DataFrame(unlabeledWordsData)
    #print(wordsData)

    tempFeatureList = ['LABEL','WORD','WORD+1','WORD-1','ABBR', 'CAP', 'NUM','LOC','PREF','SUFF','PREP','NERTAG'] #'LABEL+1','LABEL-1'
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