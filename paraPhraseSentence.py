from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet as wn
from sematch.semantic.similarity import WordNetSimilarity
from vocabulary.vocabulary import Vocabulary as vb
import json
from random import randint
import spacy
import os.path

nlp = spacy.load('en_core_web_sm')

# Function to tag sentence with part of speach
def tag(sentence):
 words = word_tokenize(sentence)
 words = pos_tag(words)
 return words

# Determine the POS to paraphrase
def paraphraseable(tag):
 return tag.startswith('NN') or tag =='VB' or tag.startswith('JJ')

# POS tagging
def pos(tag):
 if tag.startswith('NN'):
  return wn.NOUN
 elif tag.startswith('V'):
  return wn.VERB

# Function to crate synonyms using wordnet nltk
def synonyms(word, tag):
    listOfLemmas = [baseWord.lemmas() for baseWord in wn.synsets(word, pos(tag))]  
    if len(listOfLemmas) > 0:
    	listOfLemmas = listOfLemmas[0]
    	lemmas = [lemma.name().encode('ascii', 'ignore') for lemma in listOfLemmas]
    	return set(lemmas)
    else:
    	return set([])

# Create  dictonary synonums
def dictonarySynonums(word):
	synJSON = vb.synonym(word)
	if synJSON != False:
		synonyms_lists = [dictSyno["text"].encode('ascii', 'ignore') for dictSyno in json.loads(vb.synonym(word))]
		return set(synonyms_lists)
	else:
		return set([])

# controll set to calculate the semantic similarity of synonums from the base words using SPACY
def controlledSetSpacy(word,similarWords):
	utf_en_word = nlp(word.decode('utf-8', 'ignore'))
	for similarWord in similarWords.copy():
		utf_en_similarWord = nlp(similarWord.decode('utf-8','ignore'))
		if utf_en_word.similarity(utf_en_similarWord) <.76: # Variable to control accuracy of controlset 
			similarWords.discard(similarWord)
	return similarWords

# controll set to calculate the semantic similarity of synonums from the base words using WordNetSimilarity
def controlledSetWordNetSimilarity(word,similarWords):
	wns = WordNetSimilarity()
	for similarWord in similarWords.copy():
		if wns.word_similarity(word, similarWord, 'li') < 0.9996: # Variable to control accuracy of controlset
			similarWords.discard(similarWord)
	return similarWords

# to to get synonums from wordnet nltk as well as from python dictonary synonums
def synonymIfExists(sentence):
 for (word, t) in tag(sentence):
   if paraphraseable(t) and word not in ["i","I"]:
    syns = synonyms(word, t)
    syns.update(dictonarySynonums(word))
    if syns:
    	syns = controlledSetWordNetSimilarity(word,syns) # Or use the commented controlled set
    	#syns = controlledSetSpacy(word,syns)
    	if len(syns) > 1:
    		yield [word, list(syns)]
    		continue
   yield [word,[]]

# Function to get the semantic similar synonums and the total count of synonums in the entire sentence
def paraphrase(sentence):
	bagOfWords = []
	counter = 1	
	for tempArray in synonymIfExists(sentence):
		eachBoW=[]
		eachBoW.append(tempArray[0])
		eachBoW.extend(tempArray[1])
		eachBoW=list(set(eachBoW))	
		counter *= len(eachBoW)
		bagOfWords.append(eachBoW)
	return bagOfWords,counter

# Function to re-create sentence with synonums where the synonums are taken in randon order 
def paraPhraseThisSentence(sentence):
	ppList = []
	vList,count = paraphrase(sentence)
	allWordsCount = len(vList)
	for y in range(count):
		str = []
		returnStr = " "
		for w in range(allWordsCount):
			str.append(vList[w][randint(0,len(vList[w])-1)].replace("_"," "))
		ppList.append(returnStr.join(str))
	ppList = list(set(ppList))
	print (ppList)
	return ppList

paraPhraseThisSentence("Financial Institutes have always helped the society to become better version of itself.")