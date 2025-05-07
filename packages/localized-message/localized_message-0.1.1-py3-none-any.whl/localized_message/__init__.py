from pathlib import Path
from json import load as json_load
from os import environ

lang = environ.get('LANG', 'en')[:2]
_cache = {}

def json_to_dict (_file_path):
    if _file_path in _cache:
        return _cache[_file_path]
    with open(_file_path, encoding='utf-8') as f:
        data = json_load(f)
        _cache[_file_path] = data
        return data

def get_message(key, file_json='message.json'):
    if isinstance(file_json, Path):
        file_path = file_json
    elif any(char in str(file_json) for char in ('/', '\\')):
        file_path = Path(file_json)
    else:
        # Detectar el módulo que llama a get_message()
        caller_frame = inspect.stack()[1]
        caller_path = Path(caller_frame.filename).resolve()
        base_dir = caller_path.parent
        file_path = base_dir / file_json

    MESSAGE = json_to_dict(file_path)
    return MESSAGE.get(key, {}).get(
            lang, MESSAGE.get(key, {}).get(
                'en', f'[Missing error: {key}]'
                )
            )
