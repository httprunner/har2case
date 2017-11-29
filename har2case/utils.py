import io
import json
import logging
import sys

try:
    # Python3
    import urllib.parse as urlparse
    string_type = str
    ensure_ascii = False
except ImportError:
    # Python2
    import urlparse
    string_type = basestring
    ensure_ascii = True

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


def load_har_log_entries(file_path):
    """ load HAR file and return log entries list
    @return (list) entries
        [
            {
                "request": {},
                "response": {}
            },
        ]
    """
    with io.open(file_path, "r+", encoding="utf-8-sig") as f:
        try:
            content_json = json.loads(f.read())
            return content_json["log"]["entries"]
        except (KeyError, TypeError):
            logging.error("HAR file content error: {}".format(file_path))
            sys.exit(1)

def x_www_form_urlencoded(origin_dict):
    """ convert origin dict to x-www-form-urlencoded
    @param (dict) origin_dict
        {"a": 1, "b":2}
    @return (str)
        a=1&b=2
    """
    return "&".join([
        "{}={}".format(key, value)
        for key, value in origin_dict.items()
    ])

def convert_list_to_dict(origin_list):
    """ convert HAR data list to mapping
    @param (list) origin_list
        [
            {"name": "v", "value": "1"},
            {"name": "w", "value": "2"}
        ]
    @return (dict)
        {"v": "1", "w": "2"}
    """
    return {
        item["name"]: item["value"]
        for item in origin_list
    }
