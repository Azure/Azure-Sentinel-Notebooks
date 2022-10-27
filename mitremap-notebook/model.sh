#!/bin/bash
mkdir $1
cd $1
echo Downloading labels for model $1...
curl -L https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/$1/labels.json?raw=true -o "labels"
echo Downloaded labels for model $1.
echo Downloading tokenizer for model $1...
curl -L https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/$1/tokenizer?raw=true -o "tokenizer"
echo Downloaded tokenizer for model $1.
echo Downloading model dicts for model $1...
curl -L https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/$1/model_state_dicts?raw=true -o "model_state_dicts"
echo Downloaded model dicts for model $1.
