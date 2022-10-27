import utils
from utils import (
    configs as config_utils,
    storage as storage_utils,
    inference as inference_utils,
    process as process_utils
)

def go(config_widgets):
    configs = config_utils.format_user_configuration(config_widgets, verbose=True)
    if configs['ti'] == '':
        raise Exception('Please input non-empty threat intel data.')
        
    assets = storage_utils.AssetStorage('distilgpt2-512')
    inference_model = inference_utils.InferenceClassificationPipeline(assets = assets)

    processed_data_object = process_utils.ProcessData(
        configs = configs
    )

    processed_data_object.go()

    inference_df, iocs_df = inference_utils.format_predictions(
        configs = configs,
        processed_data_object = processed_data_object,
        labels = assets.labels,
        model = inference_model
    )

    return configs, inference_df, iocs_df