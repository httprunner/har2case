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
    with open(file_path, "r+") as f:
        try:
            content_json = json.loads(f.read())
            return content_json["log"]["entries"]
        except (KeyError, TypeError):
            logging.error("HAR file content error: {}".format(file_path))
            sys.exit(1)


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

    def __init__(self, file_path):
        self.log_entries = load_har_log_entries(file_path)
        self.user_agent = None
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

        parsed_object = urlparse.urlparse(entry_json["request"]["url"])
        if request_params:
            testcase_dict["request"]["params"] = request_params
            parsed_object = parsed_object._replace(query='')
            testcase_dict["request"]["url"] = parsed_object.geturl()
        else:
            testcase_dict["request"]["url"] = entry_json["request"]["url"]

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
                "request": {
                    url: "https://httprunner.top/home",
                    params: {"v": "1", "w": "2"}
                }
            }
        """
        method = entry_json["request"]["method"]
        if method == "POST":
            mimeType = entry_json["request"]["postData"]["mimeType"]
            post_data = entry_json["request"]["postData"]["text"]

            if mimeType.startswith("application/json"):
                post_data = json.loads(post_data)
                testcase_dict["request"]["json"] = post_data
            else:
                testcase_dict["request"]["data"] = post_data

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
            {"check": "status_code", "expect": entry_json["response"]["status"]}
        )

        resp_content_dict = entry_json["response"]["content"]
        encoding = resp_content_dict.get("encoding")
        text = resp_content_dict.get("text")
        mime_type = resp_content_dict["mimeType"]
        if text and mime_type.startswith("application/json"):
            if encoding and encoding == "base64":
                import base64
                resp_content_json = json.loads(base64.b64decode(text))
            else:
                resp_content_json = json.loads(text)

            for key, value in resp_content_json.items():
                if isinstance(value, (dict, list)):
                    continue

                testcase_dict["validate"].append(
                    {"check": key, "expect": value}
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
            "request": {
                "method": entry_json["request"]["method"]
            },
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
        return [
            {"test": self.make_testcase(entry_json)}
            for entry_json in self.log_entries
        ]

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
