import spacy
import sys
import os
import entitySlotClassifier




#Our wrapper.
def main():
    print("Running Main")

    path = sys.path[0]
    path = os.path.join(path,"447")

    
    analyzeFile(path)



def analyzeFile(filePath):
    print("Analyzing file: " + str(filePath))

    rawTextString = open(filePath).read()
    print(rawTextString)
    #rawTextString = rawTextString.replace("\n", " ")
    #print(rawTextString)

    nerEntityList = spacyNER(rawTextString)

    slotItems = [["ACQUIRED"],["ACQBUS"],["ACQLOC"],["DLRAMT"],["PURCHASER"],["SELLER"],["STATUS"]]

    slotItems = entitySlotClassifier.classifyNEREntities(nerEntityList,rawTextString, slotItems)
    slotItems = classifyStatus(slotItems)

    textTemplate = formatSlots(slotItems)


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


def classifyStatus(slotItems):
    print("Checking for status slot candidates")
    #Turn file into a lowercase string.
    #Remove punctuation. 

    #Check file for phrases
    #If a substring from statuses.txt appears in the text, use that substring.


def formatSlots(slotItems):
    print(slotItems)

    
main()