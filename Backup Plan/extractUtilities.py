#Extraction Utilities
import sys
import os

#Combine key files in a given directory - NOT DONE
def combineKeyFiles(filesLocation):
    print("Combining files in: " + filesLocation)
    fileNames = []


#Create a doclist of files in a given directory and save it to a file - NOT DONE
def createDocList(filesLocation):
    print("Creating doclist from files in: " + filesLocation)
    #with open('testPathList.txt', 'a') as infile: #We create a doclist of paths for testing later
    #        infile.write(os.path.join(filesLocation,filename[:-4]) + "\n")


#Create file of STATUS strings from a given gold key - NOT DONE
def createStatusFile(goldFile):
    with open(goldFile, "r") as gold:
        lines = gold.readlines()

    for line in lines:
        if "STATUS" not in line:
            lines.remove(line)
    
    for line in lines:
        if "\\" in line:
            print("MULTIPLE STATUSES DETECTED")
            #Do stuff here to split the line

    for line in lines:
        line = line[9:]
        print(line)

    with open("statuses.txt", "w") as statusFile:
        statusFile.writelines(lines)

#Read every line in a file into a list - DONE
def fileToLineList(fileDirectory):
    with open (fileDirectory, "r") as originFile:
        return originFile.readlines()

def main():
    filesLocation = sys.path[0]
    keyFilesLocation = os.path.join(filesLocation, "development-anskeys")
    rawFilesLocation = os.path.join(filesLocation, "development-docs")
    combineKeyFiles(keyFilesLocation)
    createDocList(rawFilesLocation)
    createStatusFile("keysCombined.txt")

main()