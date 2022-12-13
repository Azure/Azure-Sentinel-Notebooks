$model="distilgpt2-512"
mkdir $model
cd $model

echo Downloading labels for model $model...
Invoke-Webrequest -Uri https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/$model/labels.json -Outfile "labels"
echo Downloaded labels for model $model.

echo Downloading tokenizer for model $model...
Invoke-Webrequest -Uri https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/$model/tokenizer?raw=true -o "tokenizer"
echo Downloaded tokenizer for model $model.

echo Downloading model dicts for model $model...
Invoke-Webrequest -Uri https://github.com/microsoft/msticpy-data/blob/mitre-inference/mitre-inference-models/$model/model_state_dicts?raw=true -o "model_state_dicts"
echo Downloaded model dicts for model $model.