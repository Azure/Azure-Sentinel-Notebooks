model_options = [
    'distilgpt2-512',
    'distilgpt-1024',
    'gpt2-512',
    'gpt-1024'
]

model = 'distilgpt2-512'

bool_options = {
    'Yes': True, 'No': False
}

layout = {'width': "50%", 'height': "80px"}
style = {"description_width": "250px"}

chunk_num_sentences = 3
max_char_per_entry = 5000

number_token = 'number_token'
numberpunct_token = 'numberpunct_token'
alphanum_token = 'alphanumeric_token'
null_values = ['', '\n', 'nan', 'na', 'none', '\r', 'null']

_cyber_tokens = ['IP', 'EMAIL', 'URL', 'YARA', 'MD5_HASH', 'SHA1_HASH', 
            'SHA256_HASH', 'SHA512_HASH', 'DNS', 'PATH']

cyber_tokens = [f'{el.lower()}_token' for el in _cyber_tokens]
non_cyber_tokens = [number_token, numberpunct_token, alphanum_token]
all_tokens = cyber_tokens + non_cyber_tokens