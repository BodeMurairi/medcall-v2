#!/usr/bin/env python3

def to_dict(obj):
    """
    convert database object to normal dict
    args:
        obj: db oject
        return dict
    """
    if not obj:
        return None
    data = obj.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data
