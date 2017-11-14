import json
import os
import unittest

from har2case.core import HarParser, load_har_log_entries


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
            validators_mapping["IsSuccess"], True
        )
        self.assertEqual(
            validators_mapping["Code"], 200
        )
        self.assertEqual(
            validators_mapping["Message"], None
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
