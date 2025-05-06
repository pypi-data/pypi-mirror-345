def update_dict(origin_dict, key, value):
    assert key is not None
    if value is not None:
        origin_dict.update({key: value})
