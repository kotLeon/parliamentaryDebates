import os
import json

"""
read results from results.txt, created in main file

args: none
return: list 
"""

def readResults():

    file = open('results.txt', 'r')
    results = file.readlines()
    return results
    
"""
create dictionary from results
key: number of nodeset
value: length of all chains of premises in that nodeset

args: results created in readResults function
return: dictionary
"""
    
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

"""
creates ar updates file resultsEdited.txt
file contains dictionary created in createResultsMap function

args: dictionary created in said function
return: none
"""    

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

    
testFunction()