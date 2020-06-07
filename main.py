import os
import json
    
def iterate_and_load_AIFDB(file):
    
    data = json.loads(file.read())

    conclusions = []
    for edge in data['edges']:
        for fromNode in data['nodes']:
            if fromNode['nodeID'] == edge['fromID'] and fromNode['type'] == 'RA':
                for toNode in data['nodes']:
                    if toNode['nodeID'] == edge['toID'] and toNode['type'] == 'I':
                        conclusions.append(edge)
                            
    premises = []
    for edge in data['edges']:
        for toNode in data['nodes']:
            if toNode['nodeID'] == edge['toID'] and toNode['type'] == 'RA':
                for fromNode in data['nodes']:
                    if fromNode['nodeID'] == edge['fromID'] and fromNode['type'] == 'I':
                        premises.append(edge)
                
    return premises, conclusions, data
    
"""
find all beginning nodes in graph's premises
important: beginning premise has only 1 previous node, namely 'asserting'
important: as it appears to be a problem, near the end of the function
I eliminate all duplicates

args: list of premises, list of all edges, list of all nodes
return: list of leaves (beginning nodes)
"""
def findLeaves(premises, edges, nodes):

    leaves = []
    premiseNodes = []
    for premise in premises:
        premiseNodes.append(findNodeForEdge(premise, nodes))
            
    for premiseNode in premiseNodes:
        previousNodes = findPreviousNode(premiseNode, edges, nodes)
        if len(previousNodes) <= 1:
            leaves.append(premiseNode)
            
    # eliminate all duplicates
    leavesNoDuplicates = []
    for leaf in leaves:
        if leaf not in leavesNoDuplicates:
            leavesNoDuplicates.append(leaf)
                      
    return leavesNoDuplicates

"""
find next node for given node

args: node, list of edges, list of nodes
return: next node
"""
def findNextNode(thisNode, edges, nodes):

    nextNode = 0
   
    for edge in edges:
        if edge['fromID'] == thisNode['nodeID']:
            for node in nodes:
                if edge['toID'] == node['nodeID']:
                    nextNode = node
    return nextNode

"""
find path from given node to sink of the graph
! rephrase is ommitted!

args: node from which we start, list of all edges, list of all nodes
return: list of nodes included in the path
"""
def findPath(firstNode, edges, nodes):
    
    pathNodes = []
    
    pathNodes.append(firstNode)
    currentNode = firstNode
    nextNode = findNextNode(currentNode, edges, nodes)
    while nextNode != 0:
        importantNextNode = findNextNode(nextNode, edges, nodes)
        if nextNode['text'] == 'Default Rephrase':
            currentNode = importantNextNode
            nextNode = findNextNode(currentNode, edges, nodes)
        elif importantNextNode != 0:
            pathNodes.append(importantNextNode)
            currentNode = importantNextNode
            nextNode = findNextNode(currentNode, edges, nodes)
            if importantNextNode == pathNodes[-2]:
                break
            
    return pathNodes
    
"""
find paths for list of leaves - all paths for graph

args: list of leaves, list of all edges, list of all nodes
return list of paths (list of lists)
"""
def findAllPaths(leaves, edges, nodes):
    
    paths = []
    for leaf in leaves:
        if leaf != 0:
            paths.append(findPath(leaf, edges, nodes))
    return paths
    
"""
pretty self-explanatory: print all nodes in path

args: list of nodes
return: length of path
"""
def printPath(path):
    
    for node in path:
        print(node['nodeID'], ' ', node['text'])
    print('Length of path: ', len(path))
    
    return len(path)

"""
find previous nodes
two cases: node is text node or is function node(Default Inference, 
Default Rephrase, Default Conflict)
nodes, which take us to the right side of the graph (evil side) are excluded

args: node which previous node we want to find, list of all edges, list of all nodes
return: list of previous nodes`
"""
def findPreviousNode(thisNode, edges, nodes):

    node = [] 

    if thisNode['text'] == 'Default Inference' or thisNode['text'] == 'Default Rephrase' or thisNode['text'] == 'Default Conflict':
        for edge in edges:
            if edge['toID'] == thisNode['nodeID']:
                possibleNode = findNodeForEdge(edge, nodes)
                if possibleNode['text'] != 'Arguing' and possibleNode['text'] != 'Restating' and possibleNode['text'] != 'Disagreeing':
                    node.append(findNodeForEdge(edge, nodes))
    
    else: 
        for edge in edges:
            if edge['toID'] == thisNode['nodeID']:
                for pNode in nodes:
                    if pNode['nodeID'] == edge['fromID']:
                        node.append(pNode)
    return node   

"""
find node for edge
node which is in the beginning of this edge

args: edge, list of all nodes
return: node
"""
def findNodeForEdge(edge, nodes):
    for node in nodes:
        if node['nodeID'] == edge['fromID']:
            return node
            
"""
find all previous nodes for given conclusion
! returns nodes, which are not immediate previouses,
! but nodes with premises

args: conclusion (node), list of all edges, list of all nodes
return: list of nodes 
"""
def findPreviousesForConclusion(conclusion, edges, nodes):
    
    previouses = findPreviousNode(conclusion, edges, nodes)
    nodeText = ['Default Inference', 'Default Rephrase', 'Default Conflict']
    
    importantPreviouses = []
    for previous in previouses:
        if previous['text'] in nodeText:
            importantPreviouses.append(findPreviousNode(previous, edges, nodes)[0])
    
    return importantPreviouses

"""
find conclusion, which has most previous nodes 

args: list of conclusions, list of all edges, list of all nodes
return: string (text of conclusion), list of nodes (list of 
    its previouses)
"""
def findNodeWithMostPreviouses(conclusions, edges, nodes):
    
    conclusionNodes = []
    for conclusion in conclusions:
        for node in nodes:
            if node['nodeID'] == conclusion['toID']:
                conclusionNodes.append(node)
        
    previousNodes = []
    conclusionAndPreviouses = {}
    for conclusionNode in conclusionNodes:
        conclusionAndPreviouses[conclusionNode['text']] = findPreviousesForConclusion(conclusionNode, edges, nodes)
    
    # find the longest list in dictionary
    maxLen = 0
    maxKey = ""
    for key in conclusionAndPreviouses:
        tempLen = len(conclusionAndPreviouses[key])
        if (tempLen >= maxLen):
            maxLen = tempLen
            maxKey = key        
    
    return maxKey, conclusionAndPreviouses[maxKey]
    
"""
find conclusion with most premises for whole database

args: root, where the database is (optional)
return: number of premises (int), conclusion (string), name of 
    file, where conclusion is
"""    
def mostPreviousesForAllFiles(root='./debateTVP'):
    
    maxPrev = 0
    fileID = ""
    conclusion = ""
    resultsFile = open("resultsPreviouses.txt", "w")
    
    for file in os.listdir(root):
        if file.endswith(".json"):
            print(file)
            with open(root + '/' + file) as f:
                premises, conclusions, data = iterate_and_load_AIFDB(f)
                edges = data['edges']
                nodes = data['nodes']
                currentConclusion, prev = findNodeWithMostPreviouses(conclusions, edges, nodes)
                resultsFile.write(file)
                resultsFile.write(" ")
                resultsFile.write(str(len(prev)))
                resultsFile.write("\n")
                if len(prev) >= maxPrev:
                    maxPrev = len(prev)
                    fileID = file
                    conclusion = currentConclusion
                    
    return maxPrev, conclusion, fileID

"""
find paths for all .json files in directory

! Creates txt file results.txt, with length of all paths
! and files, where they are
! format: aaa.json
!         length_of_path

args: (optional) directory
return: none
"""
def forAllFilesInDirectory(root='./debateTVN'):
    resultsFile = open("results.txt", "w")

    for file in os.listdir(root):
        if file.endswith(".json"):
            print(file)
            with open(root + '/' + file) as f:
                premises, conclusions, data = iterate_and_load_AIFDB(f)
                edges = data['edges']
                nodes = data['nodes']
                for path in findAllPaths(findLeaves(premises, edges, nodes), edges, nodes):
                    print()
                    length = printPath(path)
                    resultsFile.write(file)
                    resultsFile.write("\n")
                    resultsFile.write(str(length))
                    resultsFile.write("\n")
            

"""
as the name says: test 
"""
def testFunction():
    # dla najdluzszych lancuchow
    #forAllFilesInDirectory()

    # dla najwiekszej liczby przeslanek
    print(mostPreviousesForAllFiles())
        
testFunction()