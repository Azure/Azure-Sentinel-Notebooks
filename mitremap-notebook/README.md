# MitreMap - Inferring MITRE Technique from Threat Intel Data

## Table of Contents
1. [Overview](#overview)
2. [Motivation](#motivation)
3. [MITRE ATT&CK Framework](#mitre-attck-framework)
4. [Goals of the MitreMap Notebook](#goals-of-the-mitremap-notebook)
5. [One-Time Setup](#one-time-setup)
    - [1. Creating a virtual environment](#1-creating-a-virtual-environment)
    - [2. Downloading model artifacts](#2-downloading-model-artifacts)
6. [Input Parameters](#input-parameters)
7. [Demo](#demo)
    - [1. MITRE Technique Inference for Threat Intel Data, WITH Model Explainability](#1-mitre-technique-inference-for-threat-intel-data-with-model-explainability)
    - [2. MITRE Technique Inference for Threat Intel Data, WITHOUT Model Explainability](#2-mitre-technique-inference-for-threat-intel-data-without-model-explainability)
8. [Use the MitreMap Notebook outside of Sentinel Notebooks](#use-the-mitremap-notebook-outside-of-sentinel-notebooks)

## Overview

This notebook allows a user to map descriptive text of an incident on to relevant MITRE ATT&CK Enterprise techniques. It uses a [GPT2](https://huggingface.co/gpt2) language model to associate terms in the description with similar descriptions in past incidents. It also extracts relevant Indicators of Compromise from the text.

You can use the notebook with one of several pre-trained models or train your own model using your own threat reports or public sources.

In order to use the notebook externally from the Sentinel-Notebooks environment, please refer to the [Use the MitreMap Notebook outside of Sentinel Notebooks](#use-the-mitremap-notebook-outside-of-sentinel-notebooks) section.
<br><br>

## Motivation

**Cyber Threat Intelligence** (CTI) provides a framework for threat analysts to document the operations of a threat actor group, and record the findings of their investigations of specific cyber attack incidents.

With the increasing number and sophistication of attacks occuring across organization's workspace, CTI allows organisations to:
- Develop a more robust and proactive security posture 
- Better detect threat vulnerabilities in their infrastructre 
- Adopt security solutions and policies that allow them to better protect their environment. 

For example **Indicators of Compromise (IoC)** represent network artifacts of a cyber intrusion and are widely used in intrusion detection systems and antivirus softwares to detect future attacks.

**Threat Intel Data** is another form of CTI which comprises of unstructured text data, describing the tools, techniques and procedures (TTPs) used by threat actor groups in a cyber operation. Historically TI data is made available to the security community in the form of *blog posts reports* and *white papers*. 

It is not scalable to manually process this growing corpus of TI data to understand the motivations capabilities and TTPs associated with an actor group. Additionally TI data does not facilitate easy extraction of IoCs which, if documented in the report, can result in the loss of known indicators in the threat intelligence corpus. 

This opens up several avenues for **Machine Learning**, more particularly **Natural Language Processing** (NLP), to identify TTPs and extract IoCs from this data.
<br><br>

## MITRE ATT&CK Framework

The **MITRE ATT&CK** framework is an openly-sourced knowledge base of TTPs used by adversaries across enterprise and mobile applications. MITRE TTPs allow people and organizations to proactively identify vulnerabilites in their system based on the behaviors, methods and patterns of activity used by an actor group in different stages of a cyber operation. More information about the kinds of tactics and techniques used by threat actors can be found [here](https://attack.mitre.org/techniques/enterprise/).

<img src="./images/mitre_map.png" alt="MITRE Enterprise Matrix" title="MITRE Enterprise Tactics and Techniques" /><br>

<br>

## Goals of the MitreMap Notebook

In this notebook we use NLP to
1. Detect *MITRE Enterprise Techniques* using the **Distil-GPT2** transformer model, &
2. Extract *IoCs* using the ```iocextract``` package, and ```msticpy```'s IoC Extractor.

from unstructured English text-based Threat Intel data. We also provide some explainability into the TTP predictions made by our NLP model by identifying specific words or phrases in the input TI data that contribute to the prediction, using [SHAP](https://arxiv.org/pdf/1705.07874.pdf) values.
<br><br>

## One-Time Setup

### 1. Creating a virtual environment

If you are running the Jupyter notebook locally, please configure a virtual environment, and download the ```../mitremap-notebook/requirements.txt``` packages in your venv from the terminal-

``` 
    > cd Azure-Sentinel-Notebooks
    > pip install virtualenv
    > virtualenv <VENV_NAME>
    > <VENV_NAME>\Scripts\activate
    > cd mitremap-notebook
    > pip install -r requirements.txt
```

Alternatively, if you are running the notebook in AML, you can create a venv using ```conda``` and download the requirements in the notebook cell using -

```
import sys
!{sys.executable} -m pip install -r requirements.txt
```

__Key packages downloaded include:__ 
- ipywidgets==7.5.1
- transformers==4.5.1
- torch==1.10.2
- msticpy==2.1.2
- nltk==3.6.2
- iocextract==1.13.1
- shap==0.41.0

If installing in a pre-built environment (Azure ML), try ```requirements.txt``` first. Due to conflicts with packages in the environment, please be prepared to dedicate the AML Compute to this notebook. If your notebook is unable to run, please install the full list of dependencies stored in ```requirements-stable.txt```.
<br><br>

### 2. Downloading model artifacts

Estimated Time: < 10 minutes

- [**Distil-GPT2**](https://huggingface.co/distilgpt2) is an English-language model, pre-trained with the smallest GPT-2 Model, and was developed using knowledge-distillation, to serve as a faster, light-weight version of GPT-2. 

- We train a Distil-GPT2 model on publicly available Threat Intel data that has been mapped to Enterprise Techniques by security experts. We have scraped data from TRAM, Sentinel Hunting and Detection Queries, Sigma, CTID, and MITRE Repositories to create our training dataset, comprising of 13k entries. The model has been trained on all 191 MITRE Enterprise techniques, but the number of entries per technique used for training varies.

- The model has been trained using a tokenizer with max length 512. The maximum length corresponds to the number of tokens in a single cyber report input which are inputted into the model, after tokenization using the GPT2 tokenizer. **We experimented with GPT2 and DistilGPT2 models with different tokenizer lengths, but found the the distilgpt2 model with 512 token lengths to have the best performance on the test data. Hence, the model artifacts are stored under the folder name ```distilgpt2-512```**.

- You can download the model artifacts using ```bash``` or ```powershell```. Either script will download the trained ```distilgpt2-512``` model artifacts from [MSTICPy's Data Repository](https://github.com/microsoft/msticpy-data/tree/mitre-inference/mitre-inference-models) to the local path ```../mitremap-notebook/distilgpt2-512/*```. Alternatively, you can use GitHub to download the model artifacts to the above local path. <br>

- The model artifacts stored locally will comprise of:<br>

    - ```./mitremap-notebook/distilgpt2-512/model_state_dicts``` - Model weights associated with the trained Distil-GPT2 Model.
    - ```./mitremap-notebook/distilgpt2-512/labels``` - Mapping of prediction labels to MITRE Enterprise Techniques.
    - ```./mitremap-notebook/distilgpt2-512/tokenizer``` - Trained Distil-GPT2 tokenizer associated with the model. <br>
<br>

- If you have access to a GPU, we HIGHLY recommend using a GPU in the inference environment. The notebook will detect the device that is used to run the notebook, and configure the model to run on that device.

**Option 1:** BASH script can be used to download the model artifacts in the notebook - ```%%bash ./model.sh``` <br>
**Option 2:** Powershell script can be used to download the model artifacts in the notebook - ```!PowerShell ./model.ps1```

<br>

### 3. Downloading the utils-1.0-py3-none-any.whl

Download the utils whl using ```%pip install utils-1.0-py3-none-any.whl``` to use the inference packages on your input data.

<br>

## Input Parameters

**IMPORTANT** In order to view the widgets in your Notebook, you **must** download the following jupyter extension via Terminal - ```jupyter labextension install @jupyter-widgets/jupyterlab-manager``` <br>

The notebook requires the following parameters from the user:

1. ***Threat Intel Data***: -
- Unstructured, English threat report that the user would like to process through the NLP model.
- The notebook will chunk the threat intel report into batches of 3 sentences, and apply the model on each batch to get the corresponding MITRE Enterprise Technique, to prevent any loss of information.

- Sample reports:

    ```    
    # 1
    Adversaries may abuse msiexec.exe to proxy execution of malicious payloads. Msiexec.exe is the command-line utility for the Windows Installer and is thus commonly associated with executing installation packages (.msi). The Msiexec.exe binary may also be digitally signed by Microsoft.
    ```

    ```
    # 2
    This query over Azure Active Directory sign-in considers all user sign-ins for each Azure Active Directory application and picks out the most anomalous change in location profile for a user within an individual application. The intent is to hunt for user account compromise, possibly via a specific applicationvector.
    ```

    ```
    # 3
    Threat actors can use auditpol binary to change audit policy configuration to impair detection capability. This can be carried out by selectively disabling/removing certain audit policies as well as restoring a custom policy owned by the threat actor.
    ```

    ```
    # 4
    When the trojan starts up it will attempt to install a scheduled task with the name of “Java Maintenance64” to keep itself running.
    ```

    ```
    # 5
    Detects exploitation attempt against Citrix Netscaler, Application Delivery Controller (ADS) and Citrix Gateway exploiting vulnerabilities reported as CVE-2020-8193 and CVE-2020-8195
    ```

2. ***Confidence Score Threshold***: 
- The TTP predictions for a sample TI input data have an associated confidence score from the NLP model, ranging from 0 (not very confident) to 1 (most confident). 
- Filter the results to predictions with confidence >= threshold configured by the user. <br>

- Default threshold: **0.6** <br> <br>

3. ***Obtain Model Explainability***: 
- Obtain further insights into which words and phrases in your input data contributed to the TTP prediction, using [SHAP](https://arxiv.org/pdf/1705.07874.pdf) values. 
- **Note**: Model Explainability will increase the time taken to obtain the inference results for your notebook! <br>

- Default value: **True** 
<br><br>

## Demo

Setting ***Obtain Model Explainability*** to **True** will increase the time taken to obtain insights for your notebook! If you are only interested in obtaining the TTP predictions for your Threat Intel data, consider setting ***Obtain Model Explainability*** to **False**.

The model predictions comprises of the following outputs:
1. ```technique``` : Unique ID associated with the predicted MITRE Enterprise ATT&CK technique.
2. ```technique_name```: Name of the above technique.
3. ```webpage_link```: Webpage link on the MITRE ATT&CK website.
4. ```confidence_score```: Confidence associated with the MITRE technique prediction, from 0 (not confident) to 1 (very confident).

<br>

Time to run the inference function will depend on the -

1. Length of the Threat Intel Report, and
2. If **Obtain Model Explainability** is set to True or False.

For our example threat reports above, time estimates are as follows -

- < 1 minute without model explainability, and 
- 1-2 minutes with model explainability.

<br>

### 1. MITRE Technique Inference for Threat Intel Data, WITH Model Explainability <br>

**Input Data Configuration:**

<img src="./images/input_1.png" alt="Input Example #1" title="Input Example #1" /><br>

**Output:**

<img src="./images/output_1.png" alt="Output Example #1" title="Output Example with Model Explanation" /><br><br>

### 2. MITRE Technique Inference for Threat Intel Data, WITHOUT Model Explainability <br>

**Input Data Configuration:**

<img src="./images/input_2.png" alt="Input Example #2" title="Input Example #1" /><br>

**Output:**

<img src="./images/output_2.png" alt="Output Example #2" title="Output Example without Model Explanation" /><br><br>

## Use the MitreMap Notebook outside of Sentinel Notebooks

In order to use the MitreMap Notebook outside the Sentinel Environment, please ensure that you also include the following files in the same directory as your notebook -

1. ```.\mitremap-notebook\requirements.txt``` - Download the external python packages to run the notebook
2. ```.\mitremap-notebook\utils-1.0-py3-none-any.whl``` - Download the utils package
3. ```.\mitremap-notebook\model.sh``` or ```.\mitremap-notebook\model.ps1``` [Optional] - Download the model artifacts using BASH or Powershell.