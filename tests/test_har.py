import json
import os
import unittest

from har2case.core import HarParser, load_har_log_entries, x_www_form_urlencoded


class TestHar(unittest.TestCase):

    @staticmethod
    def create_har_file(file_name, content):
        file_path = os.path.join(
            os.path.dirname(__file__), "data", "{}.har".format(file_name))
        with open(file_path, "w") as f:
            f.write(json.dumps(content))

        return file_path

    @classmethod
    def setUpClass(cls):
        cls.har_path = os.path.join(
            os.path.dirname(__file__), "data", "demo.har")
        cls.empty_file_path = TestHar.create_har_file(file_name="empty", content="")
        cls.empty_json_file_path = TestHar.create_har_file(file_name="empty_json", content={})

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.empty_file_path)
        os.remove(cls.empty_json_file_path)

    def test_load_har_log_entries(self):
        log_entries = load_har_log_entries(self.har_path)
        self.assertIsInstance(log_entries, list)
        self.assertIn("request", log_entries[0])
        self.assertIn("response", log_entries[0])

    def test_load_har_log_key_error(self):
        with self.assertRaises(SystemExit):
            load_har_log_entries(self.empty_json_file_path)

    def test_load_har_log_empty_error(self):
        with self.assertRaises(SystemExit):
            load_har_log_entries(self.empty_file_path)

    def test_x_www_form_urlencoded(self):
        origin_dict = {"a":1, "b": "2"}
        self.assertEqual(
            x_www_form_urlencoded(origin_dict),
            "a=1&b=2"
        )

class TestHarParser(TestHar):

    def setUp(self):
        self.har_parser = HarParser(self.har_path)
        self.log_entries = self.har_parser.log_entries

    def test_make_testcase(self):
        testcase = self.har_parser.make_testcase(self.log_entries[0])
        self.assertIn("name", testcase)
        self.assertIn("request", testcase)
        self.assertIn("validate", testcase)

        validators_mapping = {
            validator["check"]: validator["expect"]
            for validator in testcase["validate"]
        }
        self.assertEqual(
            validators_mapping["status_code"], 200
        )
        self.assertEqual(
            validators_mapping["content.IsSuccess"], True
        )
        self.assertEqual(
            validators_mapping["content.Code"], 200
        )
        self.assertEqual(
            validators_mapping["content.Message"], None
        )

    def test_make_testcases(self):
        testcases = self.har_parser.make_testcases()
        self.assertIn("name", testcases[0]["test"])
        self.assertIn("request", testcases[0]["test"])
        self.assertIn("validate", testcases[0]["test"])

    def test_gen_yaml(self):
        yaml_file = os.path.join(
            os.path.dirname(__file__), "data", "demo.yml")

        self.har_parser.gen_yaml(yaml_file)
        os.remove(yaml_file)

    def test_gen_json(self):
        json_file = os.path.join(
            os.path.dirname(__file__), "data", "demo.json")

        self.har_parser.gen_json(json_file)
        os.remove(json_file)

    def test_filter(self):
        filter_str = "httprunner"
        har_parser = HarParser(self.har_path, filter_str)
        testcases = har_parser.make_testcases()
        self.assertEqual(
            testcases[0]["test"]["request"]["url"],
            "https://httprunner.top/api/v1/Account/Login"
        )

        filter_str = "debugtalk"
        har_parser = HarParser(self.har_path, filter_str)
        testcases = har_parser.make_testcases()
        self.assertEqual(testcases, [])

    def test_exclude(self):
        exclude_str = "debugtalk"
        har_parser = HarParser(self.har_path, exclude_str=exclude_str)
        testcases = har_parser.make_testcases()
        self.assertEqual(
            testcases[0]["test"]["request"]["url"],
            "https://httprunner.top/api/v1/Account/Login"
        )

        exclude_str = "httprunner"
        har_parser = HarParser(self.har_path, exclude_str=exclude_str)
        testcases = har_parser.make_testcases()
        self.assertEqual(testcases, [])

    def test_make_request_data_params(self):
        testcase_dict = {
            "name": "",
            "request": {},
            "validate": []
        }
        entry_json = {
            "request": {
                "method": "POST",
                "postData": {
                    "mimeType": "application/x-www-form-urlencoded; charset=utf-8",
                    "params": [
                        {"name": "a", "value": 1},
                        {"name": "b", "value": "2"}
                    ]
                },
            }
        }
        self.har_parser._make_request_data(testcase_dict, entry_json)
        self.assertEqual(testcase_dict["request"]["method"], "POST")
        self.assertEqual(testcase_dict["request"]["data"], "a=1&b=2")

    def test_make_request_data_json(self):
        testcase_dict = {
            "name": "",
            "request": {},
            "validate": []
        }
        entry_json = {
            "request": {
                "method": "POST",
                "postData": {
                    "mimeType": "application/json; charset=utf-8",
                    "text": "{\"a\":\"1\",\"b\":\"2\"}"
                },
            }
        }
        self.har_parser._make_request_data(testcase_dict, entry_json)
        self.assertEqual(testcase_dict["request"]["method"], "POST")
        self.assertEqual(
            testcase_dict["request"]["json"],
            {'a': '1', 'b': '2'}
        )

    def test_make_validate(self):
        testcase_dict = {
            "name": "",
            "request": {},
            "validate": []
        }
        entry_json = {
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
                    # raw response content text is application/jose type
                    "text": "ZXlKaGJHY2lPaUpTVTBFeFh6VWlMQ0psYm1NaU9pSkJNVEk0UTBKRExV",
                    "encoding": "base64"
                }
            }
        }
        self.har_parser._make_validate(testcase_dict, entry_json)
        self.assertEqual(
            testcase_dict["validate"][0],
            {"check": "status_code", "expect": 200}
        )
