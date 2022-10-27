import string
import unicodedata
from string import printable
from typing import List, Set, Union, Dict, Tuple
import pandas as pd

import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

from nltk.corpus import stopwords 
from utils import iocs, constants

NUMBER_TOKEN = constants.number_token
NUMBERPUNCT_TOKEN = constants.numberpunct_token
ALPHANUM_TOKEN = constants.alphanum_token
NULL_VALUES = constants.null_values

STOPWORDS = set(stopwords.words('english'))

def process_string(
    text: str, 
    ignore_text_list: List[str] = [],
    flg_stop_words: bool = True, 
    flg_punctuations: bool = True,
    flg_cyber_tokens: bool = True,
    flg_stemm: bool = True, 
    flg_lemm: bool = True) -> Tuple[str, Dict]:

    """
    Preprocesses the input text to remove unwanted characters, replace some words with special/cyber tokens etc.

    :param text: text to clean
    :param additional_tokens_and_regexes: key, value pairs of cyber tokens and corresponding regexes
    :param stop_words: words to remove from the input text.
    :param ignore_text_list: ignore entries matching text in this list
    :param flg_stemm: boolean True/False for including stemming in the data processing pipeline
    :param flg_lemm: boolean True/False for including lemmatization in the data processing pipeline

    :return: processed text
    :return: iocs dictionary
    """
    ## Base Case

    if text in ignore_text_list:
        return ''

    if str(text).lower().strip() in NULL_VALUES:
        text = ''

    ## Process Text data

    iocs_dict = {}
    special_tokens = [NUMBER_TOKEN, NUMBERPUNCT_TOKEN, ALPHANUM_TOKEN]

    ## Step 1: normalise using unicodedate
    result = unicodedata.normalize("NFKD", text)

    # Step 2: Lowercase
    result = result.lower()

    # Step 3: Extract cyber_tokens
    if flg_cyber_tokens:
        result, iocs_dict = _extract_iocs_from_string(result)
        special_tokens += [f'{el.lower()}_token' for el in iocs_dict.keys()]

    # Step 4: remove non-printable characters
    result = _remove_non_printable_chars(text=result)

    # Step 5: split result into list of words using nltk
    lst = nltk.word_tokenize(result)
    
    # Step 6: Clean words in lst
    lst = [_clean_word(word) if word not in special_tokens else word for word in lst]

    # Step 7: Remove stopwords
    if flg_stop_words:
        lst = [word for word in lst if word not in set(STOPWORDS)]

    # Step 8: Remove punctuations
    if flg_punctuations:
        lst = [word for word in lst if word not in string.punctuation]

    lst_text= []

    # Step 9: Stemming (remove -ing, -ly, ...)
    if flg_stemm == True:
        ## Use the porter stemming function
        ps = nltk.stem.porter.PorterStemmer()
        lst_text = [ps.stem(word) if word not in special_tokens else word for word in lst]
                
    ## Step 10: Lemmatisation (convert the word into root word)
    if flg_lemm == True:
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        lst_text = [lem.lemmatize(word) if word not in special_tokens else word for word in lst]

    # Step 11: Join list back into string
    processed_text = ' '.join(lst_text) if lst_text else ' '.join(lst)

    return pd.Series((processed_text, iocs_dict))

def _extract_iocs_from_string(text: str):
    iocs_dict = iocs.IocPipeline().go(text, refang=False)
    for token, ioc_list in iocs_dict.items():
        token_name = f'{token.lower()}_token'
        for ioc in ioc_list:
            text = text.replace(ioc, f' {token_name} ')
    return text, iocs_dict

def _remove_non_printable_chars(text: str) -> str:
    new = ''.join(char for char in text if char in printable)
    return new

def _clean_word(word: str) -> str:  
    if word.isnumeric():
        return NUMBER_TOKEN
    has_number = any(char.isdigit() for char in word)
    has_letter = any(char.isalpha() for char in word)
    if has_number and has_letter:
        return ALPHANUM_TOKEN
    if has_number:
        return NUMBERPUNCT_TOKEN
    return word