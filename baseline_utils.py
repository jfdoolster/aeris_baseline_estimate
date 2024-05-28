
def new_dict_keyval(d: dict, key: str, val: any) -> dict:
    if key not in d:
        d[key] = val
    return d
