#Final Project

import sys
import os


#Input Processing
def main():

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


#def makeTemplates():


#TEXT: filename identifier
#ACQUIRED: entities that were acquired
#ACQBUS: the business focus of the acquired entities
#ACQLOC: the location of the acquired entities
#DLRAMT: the amount paid for the acquired entities
#PURCHASER: entities that purchased the acquired entities
#SELLER: entities that sold the acquired entities
#STATUS: status description of the acquisition event


readInput()