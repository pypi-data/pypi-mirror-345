# (C) 2025 Fujitsu Limited

import re
from typing import Optional, Any, Union

from fujitsu_quantum.config import Config
from fujitsu_quantum.storage import ObjectReference, StorageService

_snake_to_camel_pattern = re.compile(r'_([a-z])')


def snake_to_camel(snake_str: str) -> str:
    return _snake_to_camel_pattern.sub(lambda m: m.group(1).upper(), snake_str)


def snake_to_camel_keys(val: dict):
    if isinstance(val, dict):
        return {snake_to_camel(k): snake_to_camel_keys(v) for k, v in val.items()}
    else:
        return val


# From https://stackoverflow.com/a/1176023
_camel_to_snake_pattern = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')


def camel_to_snake(camel_str: str) -> str:
    return _camel_to_snake_pattern.sub('_', camel_str).lower()


def camel_to_snake_keys(val: dict):
    if isinstance(val, dict):
        return {camel_to_snake(k): camel_to_snake_keys(v) for k, v in val.items()}
    else:
        return val


def remove_none_values(dict_value: dict):
    return {k: v for k, v in dict_value.items() if v is not None}


def resolve_raw_ref(param_name: str, value: Optional[dict[str, Any]], cache: dict[str, dict[str, Any]])\
        -> Optional[Union[ObjectReference, Any]]:

    if value is None:
        return None

    if 'raw' in value:
        return value['raw']

    if 'ref' in value:
        object_path = value['ref']
        if not object_path.startswith('https://'):
            return ObjectReference(object_path[:-len(StorageService._OBJECT_EXT)])
    else:
        object_path = f'{Config.local_storage_dir}/{value["local-ref"]}'

    # TODO support lazy download; i.e., download objects when Task.<property> is called for the first time
    if object_path in cache:
        return cache[object_path][param_name]
    else:
        param_values = StorageService._download(object_path, use_local_storage=('local-ref' in value))
        cache[object_path] = param_values
        return param_values[param_name]


def numpy_to_python_types(value):
    return getattr(value, "tolist", lambda: value)()


def find_duplicates(list_value: list) -> set:
    seen = set()
    duplicates = set()
    for item in list_value:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates
