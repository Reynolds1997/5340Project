#Extraction Utilities
import sys
import os

#Combine key files in a given directory - DONE
def combineKeyFiles(filesLocation):
    print("Combining files in: " + filesLocation)
    #fileNames = []
    filenames = os.listdir(filesLocation)

    pathNames = []
    for name in filenames:
        name = os.path.join(os.curdir,filesLocation,name)
        pathNames.append(name)



    with open('keysCombined.txt', 'w') as outfile:
        for fname in pathNames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)


#Create a doclist of files in a given directory and save it to a file - DONE
def createDocList(filesLocation):
    #print("Creating doclist from files in: " + filesLocation)

    listOfFiles = os.listdir(filesLocation)
    currentDirectory = os.curdir

    with open("testPathList.txt", 'w') as testPathListFile:
        for file in listOfFiles:
            osPath = os.path.join(currentDirectory,filesLocation,file)
            osPath += "\n"
            testPathListFile.write(osPath)

    #with open('testPathList.txt', 'a') as infile: #We create a doclist of paths for testing later
    #        infile.write(os.path.join(filesLocation,filename[:-4]) + "\n")


#Create file of labelToFind strings from a given gold key - DONE
def createLabelFile(goldFile,labelToFind,outputName):
    with open(goldFile, "r") as gold:
        lines = gold.readlines()


    labelLines = []
    for line in lines:
        if labelToFind in line:
            #print(line)
            #lines.remove(line)

            labelText = line[9:-2]

            if "/" in labelText:
                #print("Multiple statuses detected")
                candidates = labelText.split("/")
                
                finalCandidates = []
                for candidate in candidates:
                    candidate = candidate.strip()
                    candidate = candidate.strip("\"")
                    candidate = candidate + "\n"
                    labelLines.append(candidate)

            elif(labelText != "-"):
                labelLines.append(labelText + "\n")
    

    
            #Do stuff here to split the line

    #for line in lines:
    #    line = line[9:-2]
        
        #print(line)

    with open(outputName, "w") as statusFile:
        statusFile.writelines(labelLines)

#Read every line in a file into a list - DONE
def fileToLineList(fileDirectory):
    with open (fileDirectory, "r") as originFile:
       # readLines = originFile.readlines()

        readLines= originFile.read().splitlines() 
       # readLines
        #print(readLines)
        return readLines


def dlramtHelper():
    moneyClues = []
    quantitativeVals = ["million","billion","mln","bln"]
    denominatorVals = ["dlrs", "dollars", "U.S. dlrs", "Canadian dlrs", "Belgian francs", "pounds sterling", "stg"]
    for quantitativeVal in quantitativeVals:
        for denominatorVal in denominatorVals:
            moneyClues.append(quantitativeVal + " " + denominatorVal)

    secondaryMoneyClues = ["undisclosed", "not disclosed"]
    return moneyClues, secondaryMoneyClues


def returnIndexes(listToCheck, searchVal):
    startAt = -1
    indexes = []
    while True:
        try:
            index = listToCheck.index(searchVal,startAt+1)
        except ValueError:
            break
        else:
            indexes.append(index)
            startAt = index
    return indexes



def main():
    filesLocation = sys.path[0]
    keyFilesLocation = os.path.join(filesLocation, "development-anskeys")
    rawFilesLocation = os.path.join(filesLocation, "development-docs")
    
    createDocList(rawFilesLocation)
    combineKeyFiles(keyFilesLocation)

    #megaKeyFile()
    
    createLabelFile("keysCombined.txt","STATUS","statuses.txt")
    createLabelFile("keysCombined.txt","ACQBUS","acqbuses.txt")


main()