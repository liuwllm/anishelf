import MeCab
import regex as re

def jpWordExtract(text):
    # Use Wakati to parse text and segment
    wakati = MeCab.Tagger("-Owakati")
    wordList = wakati.parse(text).split()
    wordDict = {}

    # Counts frequency of each word and collects info to dictionary
    for word in filter(
        checkWord,
        wordList):
        if word not in wordDict:
            wordDict[word] = 1
        else:
            wordDict[word] += 1
    
    # Sort by frequency
    wordDict = {k: v for k, v in sorted(wordDict.items(), key = lambda item: item[1], reverse=True)}

    return wordDict

# Regex to detect Japanese symbols
def checkWord(word):
    return (
        not re.match(r'^s*$', word)
        and not re.match(r'\W', word)
        and re.match(r'\p{Hiragana}|\p{Katakana}|\p{Han}', word)
    )