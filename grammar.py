# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 12:32:51 2016

@author: dkenefick
"""
from __future__ import division
import pandas as pd
import os
import re
from collections import defaultdict
import random

# personal libraries
import Creds

# path
data_path = os.path.normpath(Creds.root_path + r"\SQ.xlsm")
#out_path = os.path.normpath(Creds.root_path + r"\Python\Out\Books.xlsx")

########################
### HELPER FUNCTIONS ###
########################

def clean_text(raw_html):

    #clean html
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr,' ', raw_html)

    #clean special chars
    text_cleaner = re.compile('"|:|,|#|\(|\)|-')
    cleantext = re.sub(text_cleaner,' ', cleantext)
    
    #standardize punctuation
    text_cleaner = re.compile('\.\.\.|\?|\!|;')
    cleantext = re.sub(text_cleaner,'.', cleantext)
    
    #replace line breaks
    cleantext.replace('\n',' ')
    
    #fix periods after initials or numbered lists
    text_cleaner = re.compile('(?<= \w)\.')
    cleantext = re.sub(text_cleaner,' ', cleantext)
    
    #make periods a separate word
    cleantext = cleantext.replace('.' ,' . ')
    
    #a few other misc. replaces
    cleantext = cleantext.replace('thearrows' ,'the arrows').replace('inthailand' ,'in thailand').replace('randomizedexperiments' ,'randomized experiments').replace('howlarge','how large')
    
    return cleantext



################
### Analysis ###
################


# to generalize to huge data sets, count each row individually, synching counters as you go

# import - since used file should have all of the columns filled
data = pd.read_excel(data_path, sheetname = "Books", header = 0)

#fill in the missing values with blank strings
data['desc'].fillna(value="", inplace=True)

# All lower case
data['desc'] = data['desc'].str.lower()

# Clean HTML and special characters
data['desc'] = data['desc'].apply(clean_text)

# add review words to text according to how well the book is rated
i = 0
j=0
all_text = ""
for i in range(len(data)):
   for j in range(int(data['goodreads rating'][i])):
       all_text = all_text + ' . '+' . '+ data['desc'][i]
    
# create all pairs of words
all_words = all_text.split()
pairs = zip(all_words,all_words[1:])
next_words = defaultdict(list)

### Bigrams

# generate the 2-word version
for first, second in pairs:
    next_words[first].append(second)

#remove periods from trailing periods
next_words['.'] = [value for value in next_words['.'] if value != '.']

def get_sentence(transition_map):
    current = "."
    result = ""
    while True:
        nxt = random.choice(transition_map[current])
        result = result + nxt + " "        
        if nxt == ".":
            return result
        current = nxt


### Trigrams
trips = zip(all_words,all_words[1:],all_words[2:])
next_words_trip = defaultdict(list)
starts = []

for last, now, nxt in trips:
    if last == '.':
        starts.append(now)
    next_words_trip[(last,now)].append(nxt)
     

def get_sentence_trip(transition_map, current = random.choice(starts),prev = '.'):
    result = current +" "
    while True:
        nxt = random.choice(transition_map[prev,current])
        result = result + nxt + " "        
        if nxt == ".":
            return result
        prev = current
        current = nxt
