import json


def jsonp2json(obj: str) -> dict:
    """
    将jsonp格式的字符串转换为json格式的字符串
    :param obj: jsonp格式的字符串
    :return: json格式的字符串
    """
    if not isinstance(obj, str):
        raise ValueError("Input must be a string.")
    start_idx = obj.find("(")
    end_idx = obj.rfind(")")
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_data = obj[start_idx + 1 : end_idx].strip()
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format", obj[start_idx + 1 : end_idx])
    else:
        raise ValueError("No valid JSONP format found.")


def recursive_parse_json(data):
    """
    递归解析数据，处理字符串、字典和列表类型的数据。(如果数据很大，可能比较慢，如果要提取json中的数据，可以采用文本的方式读入，然后正则提取，而不一定要解析json)
    :param data: 输入数据，dict, list
    :return: 解析后的数据，字符串保持不变，字典和列表递归解析。
    """
    if isinstance(data, str):
        try:
            # 尝试解析字符串中的JSON对象
            parsed_data = json.loads(data)
            if isinstance(parsed_data, (dict, list)):
                return recursive_parse_json(parsed_data)
            return parsed_data
        except json.JSONDecodeError:
            return data
    elif isinstance(data, (dict, list)):
        if isinstance(data, dict):
            return {key: recursive_parse_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [recursive_parse_json(item) for item in data]
    return data
