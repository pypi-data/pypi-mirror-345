import json

from datetime import datetime


def deep_dumps(data: (dict, set, tuple, list)) -> str:
    if not isinstance(data, (dict, set, tuple, list)):
        raise TypeError('the argument(data) should be a dict/set/tuple/list')

    def dumps_datetime(data: (dict, set, tuple, list)) -> (dict, set, tuple, list):
        if isinstance(data, dict):
            for key in data.keys():
                value = data[key]
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = dumps_datetime(data=value)
            return data
        elif isinstance(data, (set, tuple, list)):
            container: list = []
            container_type: type = type(data)
            for item in data:
                if isinstance(item, datetime):
                    container.append(item.isoformat())
                else:
                    container.append(dumps_datetime(data=item))
            return container_type(container)
        else:
            return data

    result = dumps_datetime(data=data)
    return json.dumps(obj=result, ensure_ascii=False)


def deep_loads(data: (dict, set, tuple, list, str)) -> (dict, set, tuple, list):
    if not isinstance(data, (dict, set, tuple, list, str)):
        raise TypeError('the argument(data) should be a dict/set/tuple/list/str')

    if isinstance(data, str):
        load_data: (dict, set, tuple, list) = None
        try:
            try:
                load_data = json.loads(data)
                if str(load_data) == data:
                    return data
            except json.decoder.JSONDecodeError:
                return data
            return deep_loads(data=load_data)
        except json.decoder.JSONDecodeError:
            return load_data
    elif isinstance(data, dict):
        for key in data.keys():
            value = data[key]
            if isinstance(value, (dict, set, tuple, list, str)):
                data[key] = deep_loads(data=value)
        return data
    elif isinstance(data, (set, tuple, list)):
        container: list = []
        container_type: type = type(data)
        for item in data:
            if isinstance(item, (dict, set, tuple, list, str)):
                container.append(deep_loads(data=item))
            else:
                container.append(item)
        return container_type(container)
