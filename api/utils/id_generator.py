#!/usr/bin/env python3

import uuid

def generate_id():
    """generate unique id for users"""
    return str(uuid.uuid4()).split('-')[0]
