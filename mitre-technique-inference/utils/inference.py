import re
import shap
import numpy as np
import pandas as pd
from typing import List, Dict, Union
from utils import process
from transformers import TextClassificationPipeline

class InferenceClassificationPipeline():
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
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
            chunk_list = []
            for idx in range(len(outputs[i])):
                proba_list = []
                for dict in outputs[i][idx]:
                    proba_list.append(dict['score'])
                chunk_list.append(proba_list)
            logits.append(chunk_list)
        return logits

    def go(self, data, return_all_scores = False):
        outputs = []
        for test in data:
            if return_all_scores:
                output = self.classifier_all_scores(test)
            else:
                output = self.classifier_max_scores(test)
            outputs.append(output)
        return outputs

class ShapPipeline():
    def __init__(
        self, 
        classifier: TextClassificationPipeline, 
        text: Union[List[str], str], 
        outputs: Dict,
        configs: Dict
        ):
        self.classifier = classifier
        self.explainer = shap.Explainer(self.classifier)
        self.texts = text
        self.configs = configs
        self.outputs = outputs

        if not(self.configs['chunk']):
            self.texts = [self.texts]
            self.outputs = [self.outputs]

        self.base = []
        self.contribution = []
    
    def go(self):
        shap_values = self.explainer(self.texts)
        for i, text, output in zip(range(len(self.texts)), self.texts, self.outputs):
            label = output['label']

        shap_for_text = shap_values[i, :, label]
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

        shap_sentiment = {
            'positive': dict(zip(positive_data, positive_values)),
            'neutral': dict(zip(neutral_data, neutral_values)),
            'negative': dict(zip(negative_data, negative_values))
        }

        self.base.append(shap_base)
        self.contribution.append(shap_sentiment)

        if not(self.configs['chunk']):
            self.base = self.base[0]
            self.contribution = self.contribution[0]

def format_predictions(
    configs: Dict,
    processed_data_object: process.ProcessData,
    labels: Dict,
    outputs: List,
    classifier: TextClassificationPipeline
):
    inference_list = []
    ti_data = configs['ti']
    for i, elem in enumerate(ti_data):
        if max([el['score'] for el in outputs[i]]) < configs['score']:
            continue

        inference_dict = {
            'threat_intel': elem,
            'processed_threat_intel': processed_data_object.processed_data[i],
            'model': configs['model'],
            'flag_chunk': configs['chunk'],
            'flag_iocs': configs['iocs'],
            'iocs': processed_data_object.iocs[i] if configs['iocs'] else [],
            'flag_explain': configs['explain'],
            'shap_base': None,
            'shap_contribution': None
        }

        for j, output in enumerate(outputs[i]):
            technique = labels['label_to_technique'][int(output['label'].split('_')[1])]
            outputs[i][j]['technique'] = technique
            if configs['chunk']:
                outputs[i][j]['chunk'] = j+1

        if not(configs['chunk']):
            inference_dict['num_chunks'] = None
            inference_dict['output'] = outputs[i][0]
        else:
            inference_dict['num_chunks'] = len(processed_data_object.processed_data[i])
            inference_dict['output'] = outputs[i]
        
        if configs['explain']:
            shap_object = ShapPipeline(
                classifier=classifier,
                text = inference_dict['processed_threat_intel'],
                outputs= inference_dict['output'],
                configs = configs
            )
            shap_object.go()
            inference_dict['shap_base'] = shap_object.base
            inference_dict['shap_contribution'] = shap_object.contribution

        inference_list.append(inference_dict)

    if len(inference_list) > 0:    
        inference_df = pd.DataFrame(inference_list)[
            ['threat_intel', 'processed_threat_intel', 
            'flag_chunk', 'num_chunks', 'flag_iocs', 
            'iocs', 'output', 'model', 'flag_explain', 
            'shap_base', 'shap_contribution']
        ]
    else:
        inference_df = pd.DataFrame()
    return inference_df

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

def process_shap_explainability_for_row(
    inference_df,
    row_index
):
    if inference_df.empty:
        print('Empty Dataframe. No explanations available.')
        raise KeyError(f'Index {row_index} does not exist in the empty dataframe.')
        return

    try:
        data = inference_df.iloc[row_index]['threat_intel']
        processed_data = inference_df.iloc[row_index]['processed_threat_intel']
        shap_values = inference_df.iloc[row_index]['shap_base']
        output = inference_df.iloc[row_index]['output']
        contribution = inference_df.iloc[row_index]['shap_contribution']
    except:
        raise IndexError(f'Index {row_index} is not in the dataframe.')

    print(f'Inference Dataframe row index: {row_index} \n')
    print(f'Threat Intel Data: \n')
    print(data + '\n')
    
    if isinstance(shap_values, dict):
        print(f'Processed Data: ')
        print(processed_data + '\n')
        print('Predicted Label: ')
        print(output)
        print()

        shap_object = process_shap_values(shap_values)
        
        positive_contribution = len(contribution['positive'])
        negative_contribution = len(contribution['negative'])

        if (positive_contribution == 0) and (negative_contribution == 0):
            print('Insufficient shap data for explainability.')
        else:
            print('Shap Legend: {Red: Positive Contribution to Predicted Label, Blue: Negative Contribution to Predicted Label} \n')
            print('Shap Bar Plot: ')
            shap.plots.bar(shap_object)

            print('Shap Text Plot: ')
            shap.plots.text(shap_object)

            print('Positive SHAP Contribution to prediction: ')
            print(list(zip(contribution['positive'].keys(), contribution['positive'].values())))
            print()

            print('Negative SHAP Contribution to prediction: ')
            print(list(zip(contribution['negative'].keys(), contribution['negative'].values())))


    elif isinstance(shap_values, list):
        for i in range(len(shap_values)):
            print(f'Chunk #{i+1} \n')
            print(f'Processed Data: ')
            print(processed_data[i] + '\n')
            print('Predicted Label: ')
            print(output[i])
            print()

            shap_object = process_shap_values(shap_values[i])
            positive_contribution = len(contribution[i]['positive'])
            negative_contribution = len(contribution[i]['negative'])

            if (positive_contribution == 0) and (negative_contribution == 0):
                print('Insufficient shap data for explainability.')
            else:
                print('Shap Legend: {Red: Positive Contribution to Predicted Label, Blue: Negative Contribution to Predicted Label} \n')
                print('Shap Bar Plot: ')
                shap.plots.bar(shap_object)

                print('Shap Text Plot: ')
                shap.plots.text(shap_object)

                print('Positive SHAP Contribution to prediction: ')
                print(list(zip(contribution['positive'].keys(), contribution['positive'].values())))
                print()

                print('Negative SHAP Contribution to prediction: ')
                print(list(zip(contribution['negative'].keys(), contribution['negative'].values())))