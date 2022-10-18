from utils import constants
from ipywidgets import widgets

def configure_model_parameters():
    threat_intel_data_widget = widgets.Textarea(
        description='Threat Intel Report:',
        style = constants.style,
        layout = widgets.Layout(width="80%", height="200px"),
        placeholder='Input text here'
    )

    score_threshold_widget = widgets.FloatSlider(
        style = constants.style, 
        layout = widgets.Layout(width="50%", height="30px"), 
        description='Confidence Score Threshold: ', 
        min=0, 
        max=1, 
        step=0.1, 
        value=0.6
    )

    return {
        'ti': threat_intel_data_widget,
        'score': score_threshold_widget}

def format_user_configuration(all_config_widgets, verbose =True):
    configs_dict = {
        k: v.value for k, v in all_config_widgets.items()
    }

    formatted_configs = {
        'ti': configs_dict['ti'].strip(),
        'score': configs_dict['score']
    }

    if verbose:
        print('#################### SUMMARY #################### \n')

        print('Threat Intel (TI) Report: ')
        print(f"\t'{formatted_configs['ti']}'\n")

        print(f"Confidence Score Threshold: {formatted_configs['score']}\n" )

        print('################################################# \n')

    return formatted_configs