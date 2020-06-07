import os
import json

def readResults():

    file = open('results.txt', 'r')
    results = file.readlines()
    return results
    
def createResultsMap(results):
    
    resultsMap = {}
    currentKey = ' '
    for line in results:
        if line.startswith('nodeset'):
            key = line[7:12]
            if key not in resultsMap:
                resultsMap[key] = []
            currentKey = key
        else:
            if len(line) > 1:
                line = line[0:1]
            resultsMap[currentKey].append(int(line))
    
    return resultsMap                   

def printResultsToFile(resultsMap):

    resultsFile = open("resultsEdited.txt", "w")
    
    for file in resultsMap:
        resultsFile.write(file)
        for i in resultsMap[file]:
            resultsFile.write(" ")
            resultsFile.write(str(i))
        resultsFile.write("\n")
           

def testFunction():
    printResultsToFile(createResultsMap(readResults()))
    #print(map)
    #print(len(map.keys()))
    
testFunction()