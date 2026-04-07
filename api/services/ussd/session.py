#!/usr/bin/env python3

sessions = {}

def get_session(session_id):

    return sessions.get(session_id)


def save_session(session_id, data):

    sessions[session_id] = data


def clear_session(session_id):

    sessions.pop(session_id, None)
