from utils import constants
from ipywidgets import widgets

def configure_model_parameters():
    threat_intel_data_widget = widgets.Textarea(
        description='Threat Intel Data:',
        style = constants.style,
        layout = widgets.Layout(width="80%", height="200px")
    )

    model_name_widget = widgets.Select(
        options = constants.model_options, 
        style = constants.style, 
        layout = widgets.Layout(**constants.layout), 
        description='Select NLP Model: '
    )

    score_threshold_widget = widgets.FloatSlider(
        style = constants.style, 
        layout = widgets.Layout(width="50%", height="30px"), 
        description='Minimum Score Threshold: ', 
        min=0, 
        max=1, 
        step=0.1, 
        value=0.7
    )

    flag_chunks_widget = widgets.Select(
        options= list(constants.bool_options.keys()), 
        style = constants.style, 
        layout = widgets.Layout(**constants.layout), 
        description = 'Chunk Threat Intel data?: '
    )
    
    flag_iocs_widget = widgets.Select(
        options= list(constants.bool_options.keys()), 
        style = constants.style, 
        layout = widgets.Layout(**constants.layout), 
        description = 'Extract Indicators Of Compromise (IoCs)?: '
    )
    
    flag_shap_widget = widgets.Select(
        options= list(constants.bool_options.keys()), 
        style = constants.style, 
        layout = widgets.Layout(**constants.layout), 
        description = 'Get NLP Model Explainability?: '
    )

    return {
        'ti': threat_intel_data_widget,
        'model': model_name_widget,
        'score': score_threshold_widget,
        'chunk': flag_chunks_widget,
        'iocs': flag_iocs_widget,
        'explain': flag_shap_widget}

def format_user_configuration(configs_dict, verbose =True):
    formatted_configs = {
        'ti': list(filter(None, [el.strip() for el in configs_dict['ti'].split('\n\n')])),
        'model': configs_dict['model'],
        'score': configs_dict['score'],
        'chunk': constants.bool_options[configs_dict['chunk']],
        'iocs': constants.bool_options[configs_dict['iocs']],
        'explain': constants.bool_options[configs_dict['explain']]
    }

    if verbose:
        print('#################### SUMMARY #################### \n')

        print('Threat Intel (TI) Data: [\n')
        [print(f'\t"{elem}", \n') if index < len(formatted_configs['ti']) - 1 else print(f'\t"{elem}"\n') for index, elem in enumerate(formatted_configs['ti']) ]
        print(']\n')

        print(f"# of TI entries: {len(formatted_configs['ti'])}\n")
        print(f"NLP Model: {formatted_configs['model']}\n" )
        print(f"Minimum Score Threshold: {formatted_configs['score']}\n" )
        print(f"Chunk Threat Intel data?: {configs_dict['chunk']}\n")
        print(f"Extract Indicators Of Compromise (IoCs)?: {configs_dict['iocs']}\n")
        print(f"Get NLP Model Explainability?: {configs_dict['explain']}\n")

        print('################################################# \n')

    return formatted_configs