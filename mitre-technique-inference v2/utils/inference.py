import re
import shap
import numpy as np
import nltk
import copy
import pandas as pd
from typing import List, Dict, Union
from utils import process, constants, storage
from transformers import TextClassificationPipeline
from collections import defaultdict

class InferenceClassificationPipeline():
    def __init__(self, assets: storage.AssetStorage):
        self.model = assets.model
        self.tokenizer = assets.tokenizer
        self.device = assets.device.type
        
        if self.device == 'cpu':
            self.device_int = -1
        else:
            self.device_int = 1

        self.classifier_all_scores = TextClassificationPipeline(
            model = self.model.to(self.device),
            tokenizer = self.tokenizer,
            device = self.device_int,
            return_all_scores = True
        )

        self.classifier_max_scores = TextClassificationPipeline(
            model = self.model.to(self.device),
            tokenizer = self.tokenizer,
            device = self.device_int,
            return_all_scores = False
        )
    
    def get_softmax_scores(self, data):
        outputs = self.go(data, return_all_scores = True)
        logits = []
        for i in range(len(outputs)):
            proba_list = [dict['score'] for dict in outputs[i]]
            logits.append(proba_list)
        return logits

    def go(self, data, return_all_scores = False):
        outputs = []
        if return_all_scores:
            output = self.classifier_all_scores(data)
        else:
            output = self.classifier_max_scores(data)
        return output

class ShapPipeline():
    def __init__(
        self, 
        classifier: TextClassificationPipeline
        ):
        self.classifier = classifier
        self.explainer = shap.Explainer(self.classifier)
    
    def go(self, text: str, output: Dict):
        shap_values = self.explainer([text])

        shap_for_text = shap_values[0, :, output['label']]
        shap_base = {
            'values': np.round(shap_for_text.values, 5),
            'base_values': shap_for_text.base_values,
            'data': shap_for_text.data,
            'token_processed': np.array([re.sub(r'Ġ', '', el) for el in np.char.strip(shap_for_text.data)])
        }

        positive_indices = shap_base['values'] > 0
        positive_values = shap_base['values'][positive_indices]
        positive_data = shap_base['token_processed'][positive_indices]

        neutral_indices = shap_base['values'] == 0
        neutral_values = shap_base['values'][neutral_indices]
        neutral_data = shap_base['token_processed'][neutral_indices]

        negative_indices = shap_base['values'] < 0
        negative_values = shap_base['values'][negative_indices]
        negative_data = shap_base['token_processed'][negative_indices]

        shap_contribution = {
            'positive': dict(zip(positive_data, positive_values)),
            'neutral': dict(zip(neutral_data, neutral_values)),
            'negative': dict(zip(negative_data, negative_values))
        }

        return shap_base, shap_contribution

def format_predictions(
    configs: Dict,
    processed_data_object: process.ProcessData,
    labels: Dict,
    model: InferenceClassificationPipeline
):

    outputs = model.go(processed_data_object.processed_data)
    classifier = model.classifier_max_scores

    inference_list = []
    ti_data = processed_data_object.chunked_data
    flag_explainability = configs['flag_explainability']

    if flag_explainability:
        shap_obj = ShapPipeline(classifier=classifier)

    if max([el['score'] for el in outputs]) < configs['score']:
        print('The confidence score for all predictions is lower than the confidence threshold. \nResetting confidence threshold to 0.0.')
        configs['score'] = 0.0

    for i, ti_chunk in enumerate(ti_data):
        if outputs[i]['score'] < configs['score']:
            continue

        inference_dict = {
            'chunk_#': i+1,
            'sentences_#': f"{i*constants.chunk_num_sentences + 1}-{i*constants.chunk_num_sentences + 3}",
            'threat_intel': ti_chunk,
            'processed_threat_intel': processed_data_object.processed_data[i],
            'model': 'distilgpt2-512',
            'iocs': processed_data_object.iocs[i],
            'output': None,
            'shap_base': None,
            'shap_contribution': None
        }

        if i == (len(ti_data) - 1):
            inference_dict['sentences_#'] = f"{i*constants.chunk_num_sentences + 1}-{i*constants.chunk_num_sentences + len(nltk.sent_tokenize(ti_chunk))}"

        technique = labels['label_to_technique'][int(outputs[i]['label'].split('_')[1])]
        outputs[i]['confidence_score'] = round(outputs[i]['score'], 5)
        outputs[i]['technique'] = technique
        outputs[i]['technique_name'] = labels['technique_to_name'][technique]
        outputs[i]['webpage_link'] = f"https://attack.mitre.org/techniques/{technique}/"
        inference_dict['output'] = outputs[i]

        if flag_explainability:
            shap_base, shap_contribution = shap_obj.go(ti_chunk, outputs[i])
            inference_dict['shap_base'] = shap_base
            inference_dict['shap_contribution'] = shap_contribution

        inference_list.append(inference_dict)

    if len(inference_list) > 0:  
        if flag_explainability:
            columns =  ['chunk_#', 'sentences_#', 
            'threat_intel', 'processed_threat_intel', 'output', 
            'model', 'iocs', 'shap_base', 'shap_contribution']
        else:
             columns =  ['chunk_#', 'sentences_#', 
            'threat_intel', 'processed_threat_intel', 'output', 
            'model', 'iocs']

        inference_df = pd.DataFrame(inference_list)[columns]
    else:
        inference_df = pd.DataFrame()
    
    iocs_df = transform_list_of_ioc_dicts(processed_data_object.iocs)
    
    return inference_df, iocs_df

def process_shap_values(shap_dict: dict):
    shap_object = shap.Explanation(
        values = shap_dict['values'],
        data = np.array([re.sub(r'Ġ', '', el) for el in shap_dict['data']]),
        base_values = shap_dict['base_values']
    )
    return shap_object
    '''
    shap.plots.text(shap_object)
    shap.plots.bar(shap_object)
    '''

class css_style:
   BOLD = '\033[1m'
   END = '\033[0m'

def print_detailed_report(inference_df, configs):
    if inference_df.empty:
        print('No MITRE Techniques inferred from the Threat Intel data with configured confidence threshold :( \n Consider reducing your score threshold, and re-run!')
        return

    for row_index in range(len(inference_df)):
        _process_shap_explainability_for_row(
            inference_df, row_index, configs['flag_explainability']
        )

def _pprint_dict(dictionary: Dict, key_order: list = None):
    if key_order == None:
        reordered_dict = copy.deepcopy(dictionary)
    else:
        reordered_dict = {key: dictionary[key] for key in key_order if key_order}
    print('{')
    for index, key, value in zip(range(len(reordered_dict)), reordered_dict.keys(), reordered_dict.values()):
        if index == len(reordered_dict) - 1:
            print(f"\t'{key}': {value}")
        else:
            print(f"\t'{key}': {value}, ")
    print('}')

def _process_shap_explainability_for_row(
    inference_df,
    row_index,
    flag_explainability
):

    try:
        data = inference_df.iloc[row_index]['threat_intel']
        output = inference_df.iloc[row_index]['output']
        sentences_no = inference_df.iloc[row_index]['sentences_#']
        if flag_explainability:
            shap_values = inference_df.iloc[row_index]['shap_base']
            contribution = inference_df.iloc[row_index]['shap_contribution']
    except:
        raise IndexError(f'Index {row_index} is not in the dataframe.')

    print(css_style.BOLD + 'Sentences # ' + css_style.END + f': {sentences_no} \n')
    print(css_style.BOLD + 'Threat Intel Data: ' + css_style.END)
    print(data + '\n')
    print(css_style.BOLD + 'Predicted MITRE Technique: ' + css_style.END)
    _pprint_dict(output, ['technique', 'technique_name', 'webpage_link', 'confidence_score'])
    print()

    if flag_explainability or 'shap_base' in inference_df.columns:
        shap_object = process_shap_values(shap_values)
        
        positive_contribution = len(contribution['positive'])
        negative_contribution = len(contribution['negative'])
        shap_legend_dict = {'Red': 'Positive Contribution to Predicted Label', 'Blue': 'Negative Contribution to Predicted Label'}

        if (positive_contribution == 0) and (negative_contribution == 0):
            print('Insufficient shap data for explainability.')
        else:
            print(css_style.BOLD + 'Model Explainability: '  + css_style.END)
            print('Shap Legend: ')
            _pprint_dict(shap_legend_dict)
            print()

            print('Shap Text Plot: ' )
            shap.plots.text(shap_object)
            print()

            print('Top 10 tokens with Positive SHAP Contribution to predicted MITRE TTP: ')
            positive_list = list(zip(contribution['positive'].keys(), contribution['positive'].values()))
            print(positive_list[:10])
            print()

            print('Top 10 tokens with Negative SHAP Contribution to predicted MITRE TTP: ')
            negative_list = list(zip(contribution['negative'].keys(), contribution['negative'].values()))
            print(negative_list[:10])
            print()

            # print('Top Neutral SHAP Contribution to prediction: ')
            # print(list(zip(contribution['neutral'].keys(), contribution['neutral'].values())))
            # print()
    print('**************************************************')

def transform_list_of_ioc_dicts(ioc_dicts: List[Dict]):
    super_dict = defaultdict(list)

    for d in ioc_dicts:
        for k, v in d.items(): 
            super_dict[k] = list(set(super_dict[k] + v))

    super_list = []
    for key, list_iocs in dict(super_dict).items():
        if len(list_iocs) > 0:
            for ioc in list_iocs:
                super_list.append(
                    {
                        'IOC_Type': key,
                        'IOC_Value': ioc
                    }
                )
    
    if len(super_list) > 0:
        iocs_df = pd.DataFrame(super_list)
    else:
        iocs_df = pd.DataFrame()
    return iocs_df