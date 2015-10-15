#Author: Dimitry Slavin
#Name: "text_mining_toolbox2.py"
#Date Created: Monday, August 31, 2015
#General Purpose: A set of functions that make it easier to manipulate text (keyword extraction, keyword labeling, conditional filtration)
#A brief description of each function is provided below the function declaration.

def ngrams(text, n):
    #Given a string (text) and an integer (n), returns a list of all of text's n-grams
    text = text.split(' ')
    output1 = []
    for i in range(len(text)-n+1):
        output1.append(text[i:i+n])
    return output1

def flattenList(inputList):
    #Given a list of lists (list1), returns a flattened version of list1
    return [child for parent in inputList for child in parent]

def getFrequentGrams(textList, n):
    #Returns the most frequent n-grams that appear in textList
    import pandas as pd
    grams = flattenList(list(map(lambda x: ngrams(x, n), textList)))
    grams = [' '.join(gram) for gram in grams]
    return pd.Series(grams).value_counts()

#TEXT EXTRACTION
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def getHelper(text, expression):
    #Given a string (text), and a regular expression (expression), returns all matches of expression found in text
    import re
    reobj = re.compile(expression)
    outputList = reobj.findall(text)
    return outputList

def getEmails(text):
    #Returns list of emails found in text
    expression = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    return getHelper(text, expression)

def getHandles(text):
    #Returns list of handles found in text
    expression = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))(@[A-Za-z]+[A-Za-z0-9_]+)'
    return getHelper(text, expression)

def getHashtags(text):
    #Returns list of hashtags found in text
    expression = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))(#[A-Za-z]+[A-Za-z0-9_]+)'
    return getHelper(text, expression)

def getURLs(text):
    #Returns list of URLs found in text
    expression = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
    matchGroups = getHelper(text, expression)
    outputList = [matchGroup[0] for matchGroup in matchGroups]
    return outputList

def prepExpressionList(inputList):
    #Returns a modified list of regular expressions (modifications described below)
    before = r'(?<![a-zA-Z0-9-])' #aka not directly preceded by a character, number, or dash (note: ?<! also matches beginning of string)
    after = r'(?![a-zA-Z0-9-])' #aka not directly followed by character, number, or dash
    expressionList = [before+tag+after for tag in inputList]
    return expressionList

def getExpressions(text, inputList, prep = True):
    #Returns a list of all matches of the regex's found in inputList
    if isinstance(inputList, str): #if a string is passed in instead of a list, make it a list
        inputList = [inputList]
    if prep:
        expressionList = prepExpressionList(inputList)
    else:
        expressionList = inputList

    outputList = []
    for expression in expressionList:
        matches = getHelper(text, expression)
        if matches:
            outputList.extend(matches)
    return outputList

#LABELING
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def labelHelper(text, expression, label):
    #Given a string (text), a regular expression (expression), and a label, returns a modified version of text with matches labeled as label
    import re
    reobj = re.compile(expression)
    newText = reobj.sub(label, text)
    return newText

def labelURLs(text, label='{URL}'):
    #Returns text with urls labeled with label
    expression = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
    return labelHelper(text, expression, label)

def labelEmails(text, label='{EMAIL}'):
    #Returns text with emails labeled with label
    expression = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    return labelHelper(text, expression, label)

def labelHandles(text, label='{HANDLE}'):
    #Returns text with handles labeled with label
    expression = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))(@[A-Za-z]+[A-Za-z0-9_]+)'
    return labelHelper(text, expression, label)

def labelHashtags(text, label='{HASHTAG}'):
    #Returns text with hashtags labeled with label
    expression = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))(#[A-Za-z]+[A-Za-z0-9_]+)'
    return labelHelper(text, expression, label)

def labelExpressions(text, inputList, label, prep=True):
    #Returns text with all the matched expressions in inputList labeled with label
    if isinstance(inputList, str): #if a string is passed in instead of a list, make it a list
        inputList = [inputList]
    if prep:
        expressionList = prepExpressionList(inputList)
    else:
        expressionList = inputList

    newText = text #initialize newText
    for expression in expressionList:
        newText = labelHelper(newText, expression, label)
    return newText

def labelStopWords(text, label='{SW}'):
    #Returns text with all stopwords labeled with label
    import nltk
    stopwordList = nltk.corpus.stopwords.words('english')
    return labelExpressions(text, stopwordList, label)


#FILTRATION
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def filterByHelper(matchObjLists, method='AND'):
    condition = []
    length = len(matchObjLists[0]) #length of first list in matchObjLists (all lists should be the same length)

    if method == 'OR':
        for i in range(0, length):
            if any([matchObjList[i] for matchObjList in matchObjLists]):
                condition.append(True)
            else:
                condition.append(False)
        return condition

    else: # method == 'AND'
        for i in range(0, length):
            if all([matchObjList[i] for matchObjList in matchObjLists]):
                condition.append(True)
            else:
                condition.append(False)
        return condition

def filterByWordCount(textList, inputList, index = False, invert = False):
    #filter textList by word counts in inputList
    import itertools
    if isinstance(inputList, int): #if an int is passed in instead of a list, make it a list
        inputList = [inputList]

    matchObjLists = []
    for wordCount in inputList:
        matchObjList = []
        for textString in textList:
            isProperLength = len(textString.split(' ')) == wordCount
            matchObjList.append(isProperLength)
        matchObjLists.append(matchObjList)
    condition = filterByHelper(matchObjLists, method='OR')

    if invert:
        condition = [not boolVal for boolVal in condition]

    if index is False:
        return list(itertools.compress(textList, condition))
    else:
        return list(itertools.compress(enumerate(textList), condition))


def filterByExpression(textList, inputList, prep = True, method = 'AND', index = False, invert = False):
    #filter textList by expressions in inputList
    import itertools
    import re

    if isinstance(inputList, str): #if a string is passed in instead of a list, make it a list
        inputList = [inputList]
    
    if prep:
        expressionList = prepExpressionList(inputList)
    else:
        expressionList = inputList

    matchObjLists = []
    for expression in expressionList:
        matchObjList = []
        for textString in textList:
            matchObjList.append(re.search(expression, textString))
        matchObjLists.append(matchObjList)
    condition = filterByHelper(matchObjLists, method = method)

    if invert:
        condition = [not boolVal for boolVal in condition]

    if index is False:
        return list(itertools.compress(textList, condition))
    else:
        return list(itertools.compress(enumerate(textList), condition))

