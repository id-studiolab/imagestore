import re
from datetime import datetime
from zope.security.management import getInteraction

def get_request():
    return getInteraction().participations[0]

def liberal_parse_iso_to_datetime(datestamp):
    # add time if only date given
    if 'T' not in datestamp:
        return parse_iso_to_datetime(datestamp + 'T00:00:00.0')
    time_segments = len(datestamp.split(':'))
    if time_segments == 1:
        # only hour given, add minutes, second, ms
        return parse_iso_to_datetime(datestamp + ':00:00.0')
    elif time_segments == 2:
        # only minute given, add seconds, ms
        return parse_iso_to_datetime(datestamp + ':00.0')
    # add microsecond if none given
    if '.' not in datestamp:
        return parse_iso_to_datetime(datestamp + '.0')
    return parse_iso_to_datetime(datestamp)

def parse_iso_to_datetime(datestamp):
    splitted = datestamp.split('T')
    if len(splitted) == 2:
        d, t = splitted
        if not t:
            raise ValueError
    else:
        d = splitted[0]
        t = '00:00:00.0'
    YYYY, MM, DD = d.split('-')
    hh, mm, ss = t.split(':') # this assumes there's no timezone info
    ss, ms = ss.split('.')
    return datetime(
        int(YYYY), int(MM), int(DD), int(hh), int(mm), int(ss), int(ms))

NAME_RE = re.compile('^[a-zA-Z0-9_\.\-]*$')

def is_legal_name(name):
    return NAME_RE.match(name) is not None
