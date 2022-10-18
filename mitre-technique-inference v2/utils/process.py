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
        self.chunk_len = constants.chunk_num_sentences
        self.data = self.configs['ti']
        
        self.chunked_data = []
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
        split_into_sentences = nltk.sent_tokenize(self.data)
        chunks_of_sentences = list(
                ProcessData.divide_chunks(split_into_sentences, self.chunk_len)
            )

        processed_text = []
        for i, chunk in enumerate(chunks_of_sentences):
            processed_text.append(strings.process_string(
                text = chunk,
                flg_stop_words=True,
                flg_cyber_tokens=True,
                flg_punctuations = False,
                flg_stemm = True,
                flg_lemm = True
            ))
        
        processed_strings = []
        iocs_list = []

        for chunk in processed_text:
            mini_chunk = ProcessData.process_sentences(chunk[0], tokens)
            iocs_list.append(chunk[1])
            processed_strings.append(' '.join(mini_chunk))
        
        for i, item in enumerate(processed_strings):
            processed_strings[i] = processed_strings[i][:constants.max_char_per_entry]

        return chunks_of_sentences, processed_strings, iocs_list

    def _go(self):
        chunks_of_sentences, processed_data, iocs_list = self._process_data_into_chunks()
        self.chunked_data = chunks_of_sentences
        self.processed_data = processed_data
        self.iocs = iocs_list
    
    def go(self):
        self._go()