#!/bin/bash
mkdir distilgpt2-512
cd distilgpt2-512
echo Downloading labels for model distilgpt2-512...
curl -L https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/distilgpt2-512/labels.json?raw=true -o "labels"
echo Downloaded labels for model distilgpt2-512.
echo Downloading tokenizer for model distilgpt2-512...
curl -L https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/distilgpt2-512/tokenizer?raw=true -o "tokenizer"
echo Downloaded tokenizer for model distilgpt2-512.
echo Downloading model dicts for model distilgpt2-512...
curl -L https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/distilgpt2-512/model_state_dicts?raw=true -o "model_state_dicts"
echo Downloaded model dicts for model distilgpt2-512.
