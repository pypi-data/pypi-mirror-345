import re


def format_list(ls: list):
    result = []
    for item in ls:
        if isinstance(item, list):
            result.append(format_list(item))
        elif isinstance(item, dict):
            result.append(format_dict(item))
        elif isinstance(item, RequestModel):
            result.append(item.model_to_dict())
        else:
            result.append(item)
    return result


def format_dict(obj: dict):
    result = {}
    for k, v in obj.items():
        format_key = to_upper_camel_case(k)
        if isinstance(v, list):
            result[format_key] = format_list(v)
        elif isinstance(v, dict):
            result[format_key] = format_dict(v)
        elif isinstance(v, RequestModel):
            result[format_key] = v.model_to_dict()
        else:
            result[format_key] = v
    return result


def to_upper_camel_case(s):
    l = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), s.lower())
    return l[0].upper() + l[1:]


class RequestModel(object):

    def model_to_dict(self):
        result = {}
        common_dict = self.__dict__
        for key, value in common_dict.items():
            format_key = to_upper_camel_case(key)
            if isinstance(value, list):
                result[format_key] = format_list(value)
            elif isinstance(value, dict):
                result[format_key] = format_dict(value)
            elif isinstance(value, RequestModel):
                result[format_key] = value.model_to_dict()
            else:
                result[format_key] = value
        return result

    def __str__(self):
        return str(self.model_to_dict())
