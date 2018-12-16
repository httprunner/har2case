# har2case

[![LICENSE](https://img.shields.io/github/license/HttpRunner/har2case.svg)](https://pypi.org/project/har2case/) [![travis-ci](https://travis-ci.org/HttpRunner/har2case.svg?branch=master)](https://travis-ci.org/HttpRunner/har2case) [![coveralls](https://coveralls.io/repos/github/HttpRunner/har2case/badge.svg?branch=master)](https://coveralls.io/github/HttpRunner/har2case?branch=master) [![pypi version](https://img.shields.io/pypi/v/har2case.svg)](https://pypi.python.org/project/har2case/) [![pyversions](https://img.shields.io/pypi/pyversions/har2case.svg)](https://pypi.python.org/project/har2case/)

Convert HAR(HTTP Archive) to YAML/JSON testcases for HttpRunner.


## install

`har2case` is available on `PyPI` and can be installed through pip or easy_install.

```bash
$ pip install har2case
```

or

```bash
$ easy_install har2case
```

## usage

When `har2case` is installed, a **har2case** command should be available in your shell (if you're not using
virtualenv—which you should—make sure your python script directory is on your path).

To see `har2case` version:

```bash
$ har2case -V
0.2.0
```

To see available options, run:

```text
$ har2case -h
usage: main.py [-h] [-V] [--log-level LOG_LEVEL] [-2y] [--filter FILTER]
               [--exclude EXCLUDE]
               [har_source_file]

Convert HAR to YAML/JSON testcases for HttpRunner.

positional arguments:
  har_source_file       Specify HAR source file

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show version
  --log-level LOG_LEVEL
                        Specify logging level, default is INFO.
  -2y, --to-yml, --to-yaml
                        Convert to YAML format, if not specified, convert to
                        JSON format by default.
  --filter FILTER       Specify filter keyword, only url include filter string
                        will be converted.
  --exclude EXCLUDE     Specify exclude keyword, url that includes exclude
                        string will be ignored, multiple keywords can be
                        joined with '|'
```

## examples

In most cases, you can only specify har source file path. By default, `har2case` will generate testcase file in JSON format.

```bash
$ har2case tests/data/demo.har
INFO:root:Start to generate testcase.
INFO:root:dump testcase to JSON format.
INFO:root:Generate JSON testcase successfully: tests/data/demo.json
```

If you want to generate testcase file in YAML format, you can add `-2y` or `--to-yml` argument.

```bash
$ har2case tests/data/demo.har -2y
INFO:root:Start to generate testcase.
INFO:root:dump testcase to YAML format.
INFO:root:Generate YAML testcase successfully: tests/data/demo.yaml
```

The generated testcase file is in the same folder with the har source file and has the same name.

**filter**

You can do some filter while conversion, only url that includes filter string will be converted.

```bash
$ har2case tests/data/demo.har --filter httprunner.top
```

**exclude**

You can also set exclude keyword while conversion, url that includes exclude string will be ignored.

```bash
$ har2case tests/data/demo.har --exclude debugtalk.com
```

## generated testcase

Generated YAML testcase `demo.yml` shows like below:

```yaml
-   config:
        name: testcase description
        variables: {}
-   test:
        name: /api/v1/Account/Login
        request:
            headers:
                Content-Type: application/json
                User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36
                    (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
            json:
                Pwd: '123'
                UserName: test001
                VerCode: ''
            method: POST
            url: https://httprunner.top/api/v1/Account/Login
        validate:
        -   eq:
            - status_code
            - 200
        -   eq:
            - headers.Content-Type
            - application/json; charset=utf-8
        -   eq:
            - content.IsSuccess
            - true
        -   eq:
            - content.Code
            - 200
        -   eq:
            - content.Message
            - null
```

And generated JSON testcase `demo.json` shows like this:

```json
[
    {
        "config": {
            "name": "testcase description",
            "variables": {}
        }
    },
    {
        "test": {
            "name": "/api/v1/Account/Login",
            "request": {
                "url": "https://httprunner.top/api/v1/Account/Login",
                "method": "POST",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                    "Content-Type": "application/json"
                },
                "json": {
                    "UserName": "test001",
                    "Pwd": "123",
                    "VerCode": ""
                }
            },
            "validate": [
                {
                    "eq": [
                        "status_code",
                        200
                    ]
                },
                {
                    "eq": [
                        "headers.Content-Type",
                        "application/json; charset=utf-8"
                    ]
                },
                {
                    "eq": [
                        "content.IsSuccess",
                        true
                    ]
                },
                {
                    "eq": [
                        "content.Code",
                        200
                    ]
                },
                {
                    "eq": [
                        "content.Message",
                        null
                    ]
                }
            ]
        }
    }
]
```