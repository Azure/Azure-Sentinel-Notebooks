import re
import copy
import string
import nltk
from utils import constants, strings
from itertools import chain
from typing import List, Dict

class ProcessData():
    def __init__(self, configs: Dict):
        self.configs = configs
        if self.configs['chunk']:
            self.chunk_len = constants.chunk_num_sentences
        else:
            self.chunk_len = None

        self.data = self.configs['ti']
        if isinstance(self.data, str):
            self.data = [self.data]
        
        self.processed_data = []
        self.iocs = []
    
    @staticmethod
    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield ' '.join(l[i:i + n])
    
    @staticmethod
    def process_sentences(text, tokens):
        orig_sentences = nltk.sent_tokenize(text)
        for idx, sentence in enumerate(orig_sentences):
            copy = sentence
            for token in tokens:
                copy = re.sub(token, '', copy)
            copy_split = copy.split()
            for i, el in enumerate(copy_split):
                copy_split[i] = el.translate(str.maketrans('', '', string.punctuation))
            orig_sentences[idx] = sentence if len(list(filter(None, copy_split))) > 0 else ''
        processed_orig_sentences = list(filter(None, orig_sentences))
        return processed_orig_sentences 
    
    def _process_data_into_chunks(self):
        tokens = constants.all_tokens
        split_into_sentences = [nltk.sent_tokenize(text) for text in self.data]
        chunks_of_sentences = [
            list(
                ProcessData.divide_chunks(split_into_sentences[i], self.chunk_len)
            ) for i in range(len(split_into_sentences))
        ]

        processed_text = []
        for i, chunk in enumerate(chunks_of_sentences):
            processed_text.append([strings.process_string(
                text = text_str,
                flg_stop_words=True,
                flg_cyber_tokens=True,
                flg_punctuations = False,
                flg_stemm = True,
                flg_lemm = True
            ) for text_str in chunk])
        
        processed_strings = []
        iocs_list = []

        for chunk in processed_text:
            mini_chunk = list(
                ProcessData.process_sentences(elem[0], tokens) for elem in chunk
            )

            for idx, elem in enumerate(mini_chunk):
                mini_chunk[idx] = [' '.join(elem)]

            if self.configs['iocs']:
                iocs_list.append([el[1] for el in chunk])

            processed_strings.append(list(chain.from_iterable(mini_chunk)))
        return processed_strings, iocs_list
    
    def _process_data(self):
        tokens = constants.all_tokens
        processed_text= [strings.process_string(
            text = text_str,
            flg_stop_words=True,
            flg_cyber_tokens=True,
            flg_punctuations = False,
            flg_stemm = True,
            flg_lemm = True
        ) for text_str in self.data]

        strings_list = [el[0] for el in processed_text]
        iocs_list = []
        if self.configs['iocs']:
            iocs_list = [el[1] for el in processed_text]
        
        processed_strings = [
            ' '.join(list(ProcessData.process_sentences(elem, tokens))) for elem in strings_list
        ]

        return processed_strings, iocs_list


    def _go(self):
        if self.configs['chunk']:
            processed_data, iocs_list = self._process_data_into_chunks()
        else:
            processed_data, iocs_list = self._process_data()
        
        for i, item in enumerate(processed_data):
            if isinstance(item, str):
                processed_data[i] = processed_data[i][:constants.max_char_per_entry]
            else:
                for j, item_j in enumerate(processed_data[i]):
                    processed_data[i][j] = processed_data[i][j][:constants.max_char_per_entry]
        
        self.processed_data = processed_data
        self.iocs = iocs_list
    
    def go(self):
        self._go()