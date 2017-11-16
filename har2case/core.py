import io
import json
import logging
import sys

import yaml

try:
    # Python3
    import urllib.parse as urlparse
    string_type = str
except ImportError:
    # Python2
    import urlparse
    string_type = basestring


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

class HarParser(object):

    IGNORE_HEADERS = [
        "host",
        "accept",
        "content-length",
        "connection",
        "accept-encoding",
        "accept-language",
        "origin",
        "referer",
        "cache-control",
        "pragma",
        "cookie",
        "upgrade-insecure-requests",
        ":authority",
        ":method",
        ":scheme",
        ":path"
    ]

    def __init__(self, file_path, filter_str=None, exclude_str=None):
        self.log_entries = load_har_log_entries(file_path)
        self.user_agent = None
        self.filter_str = filter_str
        self.exclude_str = exclude_str
        self.testset = self.make_testset()

    def _make_request_url(self, testcase_dict, entry_json):
        """ parse HAR entry request url and queryString, and make testcase url and params
        @param (dict) entry_json
            {
                "request": {
                    "url": "https://httprunner.top/home?v=1&w=2",
                    "queryString": [
                        {"name": "v", "value": "1"},
                        {"name": "w", "value": "2"}
                    ],
                },
                "response": {}
            }
        @output testcase_dict:
            {
                "name: "/home",
                "request": {
                    url: "https://httprunner.top/home",
                    params: {"v": "1", "w": "2"}
                }
            }
        """
        request_params = {}
        query_string_list = entry_json["request"].get("queryString", [])
        for query_string in query_string_list:
            request_params[query_string["name"]] = query_string["value"]

        url = entry_json["request"].get("url")
        if not url:
            logging.exception("url missed in request.")
            sys.exit(1)

        parsed_object = urlparse.urlparse(url)
        if request_params:
            testcase_dict["request"]["params"] = request_params
            parsed_object = parsed_object._replace(query='')
            testcase_dict["request"]["url"] = parsed_object.geturl()
        else:
            testcase_dict["request"]["url"] = url

        testcase_dict["name"] = parsed_object.path

    def _make_request_headers(self, testcase_dict, entry_json):
        """ parse HAR entry request headers, and make testcase headers.
            header in IGNORE_HEADERS will be ignored.
        @param (dict) entry_json
            {
                "request": {
                    "headers": [
                        {"name": "Host", "value": "httprunner.top"},
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "User-Agent", "value": "iOS/10.3"}
                    ],
                },
                "response": {}
            }
        @output testcase_dict:
            {
                "request": {
                    headers: {"Content-Type": "application/json"}
                }
            }
        """
        testcase_headers = {}
        for header in entry_json["request"].get("headers", []):
            if header["name"].lower() in self.IGNORE_HEADERS:
                continue
            if header["name"].lower() == "user-agent":
                if not self.user_agent:
                    self.user_agent = header["value"]
                continue

            testcase_headers[header["name"]] = header["value"]

        if testcase_headers:
            testcase_dict["request"]["headers"] = testcase_headers

    def _make_request_data(self, testcase_dict, entry_json):
        """ parse HAR entry request data, and make testcase request data
        @param (dict) entry_json
            {
                "request": {
                    "method": "POST",
                    "postData": {
                        "mimeType": "application/x-www-form-urlencoded; charset=utf-8",
                        "params": [
                            {"name": "a", "value": 1},
                            {"name": "b", "value": "2"}
                        }
                    },
                },
                "response": {...}
            }
        @output testcase_dict:
            {
                "request": {
                    "method": "POST",
                    "data": {"v": "1", "w": "2"}
                }
            }
        """
        method = entry_json["request"].get("method")
        if not method:
            logging.exception("method missed in request.")
            sys.exit(1)

        testcase_dict["request"]["method"] = method
        if method == "POST":
            mimeType = entry_json["request"].get("postData", {}).get("mimeType")

            # Note that text and params fields are mutually exclusive.
            params = entry_json["request"].get("postData", {}).get("params", [])
            text = entry_json["request"].get("postData", {}).get("text")
            if text:
                post_data = text
            else:
                post_data = {
                    param["name"]: param["value"]
                    for param in params
                }

            request_data_key = "data"
            if not mimeType:
                pass
            elif mimeType.startswith("application/json"):
                post_data = json.loads(post_data)
                request_data_key = "json"
            elif mimeType.startswith("application/x-www-form-urlencoded"):
                post_data = x_www_form_urlencoded(post_data)
            else:
                #TODO: make compatible with more mimeType
                pass

            testcase_dict["request"][request_data_key] = post_data

    def _make_validate(self, testcase_dict, entry_json):
        """ parse HAR entry response and make testcase validate.
        @param (dict) entry_json
            {
                "request": {},
                "response": {
                    "status": 200,
                    "headers": [
                        {
                            "name": "Content-Type",
                            "value": "application/json; charset=utf-8"
                        },
                    ],
                    "content": {
                        "size": 71,
                        "mimeType": "application/json; charset=utf-8",
                        "text": "eyJJc1N1Y2Nlc3MiOnRydWUsIkNvZGUiOjIwMCwiTWVzc2FnZSI6bnVsbCwiVmFsdWUiOnsiQmxuUmVzdWx0Ijp0cnVlfX0=",
                        "encoding": "base64"
                    }
                }
            }
        @output testcase_dict:
            {
                "validate": [
                    {"check": "status_code", "expect": 200}
                ]
            }
        """
        testcase_dict["validate"].append(
            {"check": "status_code", "expect": entry_json["response"].get("status")}
        )

        resp_content_dict = entry_json["response"].get("content")
        encoding = resp_content_dict.get("encoding")
        text = resp_content_dict.get("text")
        mime_type = resp_content_dict["mimeType"]
        if text and mime_type.startswith("application/json"):
            if encoding and encoding == "base64":
                import base64
                content = base64.b64decode(text)
                resp_content_json = json.loads(content.decode('utf-8'))
            else:
                resp_content_json = json.loads(text)

            for key, value in resp_content_json.items():
                if isinstance(value, (dict, list)):
                    continue

                testcase_dict["validate"].append(
                    {"check": "content.{}".format(key), "expect": value}
                )

    def make_testcase(self, entry_json):
        """ extract info from entry dict and make testcase
        @param (dict) entry_json
            {
                "request": {
                    "method": "POST",
                    "url": "https://httprunner.top/api/v1/Account/Login",
                    "headers": [],
                    "queryString": [],
                    "postData": {},
                },
                "response": {
                    "status": 200,
                    "headers": [],
                    "content": {}
                }
            }
        """
        testcase_dict = {
            "name": "",
            "request": {},
            "validate": []
        }

        self._make_request_url(testcase_dict, entry_json)
        self._make_request_headers(testcase_dict, entry_json)
        self._make_request_data(testcase_dict, entry_json)
        self._make_validate(testcase_dict, entry_json)

        return testcase_dict

    def make_testcases(self):
        """ extract info from HAR log entries list and make testcase list
        """
        testcases = []
        for entry_json in self.log_entries:
            url = entry_json["request"].get("url")
            if self.filter_str and self.filter_str not in url:
                continue

            if self.exclude_str and self.exclude_str in url:
                continue

            testcases.append(
                {"test": self.make_testcase(entry_json)}
            )

        return testcases

    def make_config(self):
        """ sets config block of testset
        """
        config_dict = {
            "name": "testset description",
            "variables": [],
            "headers": {}
        }
        config_dict["headers"]["User-Agent"] = self.user_agent

        return {"config": config_dict}

    def make_testset(self):
        """ Extract info from HAR file and prepare for testcase
        """
        logging.debug("Extract info from HAR file and prepare for testcase.")
        testset = self.make_testcases()
        config = self.make_config()
        testset.insert(0, config)
        return testset

    def gen_yaml(self, yaml_file):
        """ dump HAR entries to yaml testset
        """
        logging.debug("Start to generate YAML testset.")

        with open(yaml_file, 'w') as outfile:
            yaml.dump(self.testset, outfile, default_flow_style=False, indent=4)

        logging.info("Generate YAML testset successfully: {}".format(yaml_file))

    def gen_json(self, json_file):
        """ dump HAR entries to json testset
        """
        logging.debug("Start to generate JSON testset.")

        with open(json_file, 'w') as outfile:
            json.dump(self.testset, outfile, indent=2)

        logging.info("Generate JSON testset successfully: {}".format(json_file))
