import os
import json
import artifacts
import joblib
import torch
from utils import constants
from transformers import GPT2ForSequenceClassification

class AssetStorage():
    storage_folder = artifacts.__path__[0]
    def __init__(self, model_name: str = None):
        self.model_name = constants.model if model_name == None else model_name
        
        self.artifacts_path = os.path.join(self.storage_folder, model_name)

        self.tokenizer = self.download_tokenizer()
        self.labels = self.download_labels()
        self.model, self.device = self.download_model()
    
    def download_model(self):
        self.model_path = os.path.join(self.artifacts_path, 'model_state_dicts')
        model = GPT2ForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path = self.model_name.split('-')[0],
            num_labels = len(self.labels['technique_to_label'])
        )

        model.resize_token_embeddings(len(self.tokenizer))
        model.config.pad_token_id = model.config.eos_token_id
        model.load_state_dict(torch.load(self.model_path))
        model.eval()

        device_str = 'cuda' if torch.cuda.is_available() else 'cpu'
        device = torch.device(device_str)
        model.to(device)
        
        print(f"Model artifact obtained from path {self.model_path}")
        print(f"Model on device '{device}'")
        return model, device
    
    def download_tokenizer(self):
        self.tokenizer_path = os.path.join(self.artifacts_path, 'tokenizer')
        tokenizer = joblib.load(self.tokenizer_path)
        print(f"Tokenizer artifact obtained from path {self.tokenizer_path}")
        return tokenizer
    
    def download_labels(self):
        self.labels_path = os.path.join(self.artifacts_path, 'labels')
        labels = json.load(open(self.labels_path, "r"))
        labels['label_to_technique'] = {int(key): value for key, value in labels['label_to_technique'].items()}
        print(f"Labels artifact obtained from path {self.labels_path}")
        return labels