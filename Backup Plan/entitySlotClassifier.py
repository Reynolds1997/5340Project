


#Classifies NER entities
def classifyNEREntities(nerEntities, rawText, entityLabelList):

    
    #print("Running entity slot classifier")
    print(nerEntities)

    for entity in nerEntities:
        entityWord = entity[0]
        entityLabel = entity[1]
        #if entityLabel == "ORG":
        #if entityLabel == "GPE"
        #if entityLabel
        entityLabelList[2].append(entityWord) #For now, we throw everything under the location label

    return entityLabelList