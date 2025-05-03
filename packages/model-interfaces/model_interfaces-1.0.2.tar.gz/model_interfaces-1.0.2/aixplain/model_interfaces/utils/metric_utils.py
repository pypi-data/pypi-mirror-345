__author__='thiagocastroferreira'

import re

from typing import List

def remove_punctuation(lst:List):
    no_punc_lst = []
    for e in lst:
        tmp = re.sub(r'[^\w\s]', '', str(e))
        if tmp:
            no_punc_lst.append(tmp)
        else:
            no_punc_lst.append(e)
    return no_punc_lst

def lowercase(lst:List):
    lower_case_lst = []
    for e in lst:
        lower_case_lst.append(str(e).lower())
    return lower_case_lst

def transpose(lst:List):
    # transposing the references for sentence-level scores and jitter library
    nreferences = len(lst[0])
    transposed = []
    for i in range(nreferences):
        transposed.append([ref[i] for ref in lst])
    return transposed

def remove_numbers(text:str):
    tmp = re.sub(
        r'(([\d\u0660-\u0669\u06F0-\u06F9]+([.,/][\d\u0660-\u0669\u06F0-\u06F9]+)?([%\u066A])?)|(^[.,][\d\u0660-\u0669\u06F0-\u06F9]+([%\u066A])?))',
        ' ', text, flags=re.UNICODE)
    tmp = re.sub(r' +', ' ', tmp).strip()
    return tmp

def remove_urls(text:str):
    tmp = re.sub(
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
        ' ', text)
    tmp = re.sub(r' +', ' ', tmp).strip()
    return tmp

def remove_emails(text:str):
    tmp = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", ' ', text)
    tmp = re.sub(r' +', ' ', tmp).strip()
    return tmp 

def remove_emojis(text:str):
    emojis = re.compile("["
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F1E0-\U0001F1FF"  # flags 
                        "]+", flags=re.UNICODE)
    tmp = emojis.sub(r' ', text)
    tmp = re.sub(r' +', ' ', tmp).strip()
    return tmp