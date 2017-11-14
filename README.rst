har2case
========

.. image:: https://img.shields.io/github/license/HttpRunner/har2case.svg
    :target: https://github.com/HttpRunner/har2case/blob/master/LICENSE

.. image:: https://travis-ci.org/HttpRunner/har2case.svg?branch=master
    :target: https://travis-ci.org/HttpRunner/har2case

.. image:: https://coveralls.io/repos/github/HttpRunner/har2case/badge.svg?branch=master
    :target: https://coveralls.io/github/HttpRunner/har2case?branch=master

.. image:: https://img.shields.io/pypi/v/har2case.svg
    :target: https://pypi.python.org/pypi/har2case

.. image:: https://img.shields.io/pypi/pyversions/har2case.svg
    :target: https://pypi.python.org/pypi/har2case


Convert HAR(HTTP Archive) to YAML/JSON testcases for HttpRunner.


install
-------

``har2case`` is available on `PyPI`_ and can be installed through pip or easy_install. ::

    $ pip install har2case

or ::

    $ easy_install har2case


usage
-----

When ``har2case`` is installed, a **har2case** command should be available in your shell (if you're not using
virtualenv—which you should—make sure your python script directory is on your path).

To see ``har2case`` version: ::

    $ har2case -V
    0.0.3

To see available options, run: ::

    $ har2case -h
    usage: har2case [-h] [-V] [--log-level LOG_LEVEL]
                    [har_source_file] [output_testset_file]

    Convert HAR to YAML/JSON testcases for HttpRunner.

    positional arguments:
    har_source_file       Specify HAR source file
    output_testset_file  Optional. Specify converted YAML/JSON testcase file.

    optional arguments:
    -h, --help            show this help message and exit
    -V, --version         show version
    --log-level LOG_LEVEL
                          Specify logging level, default is INFO.


examples
--------

In most cases, you can run ``har2case`` like this: ::

    $ har2case tests/data/demo.har demo.yml
    INFO:root:Generate YAML testset successfully: demo.yml

    $ har2case tests/data/demo.har demo.json
    INFO:root:Generate JSON testset successfully: demo.json

As you see, the first parameter is HAR source file path, and the second is converted YAML/JSON file path.

The output testset file type is detemined by the suffix of your specified file.

If you only specify HAR source file path, the output testset is in JSON format by default and located in the same folder with source file. ::

    $ har2case tests/data/demo.har
    INFO:root:Generate JSON testset successfully: tests/data/demo.json

Generated YAML testset ``demo.yml`` shows like below:

.. code-block:: yaml

    -   config:
            headers:
                User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36
                    (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
            name: testset description
            variables: []
    -   test:
            name: /api/v1/Account/Login
            request:
                headers:
                    Content-Type: application/json
                json:
                    Pwd: '123'
                    UserName: test001
                    VerCode: ''
                method: POST
                url: https://httprunner.top/api/v1/Account/Login
            validate:
            -   check: status_code
                expect: 200
            -   check: IsSuccess
                expect: true
            -   check: Code
                expect: 200
            -   check: Message
                expect: null

And generated JSON testset ``demo.json`` shows like this:

.. code-block:: json

    [
        {
            "config": {
                "name": "testset description",
                "variables": [],
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
                }
            }
        },
        {
            "test": {
                "name": "/api/v1/Account/Login",
                "request": {
                    "method": "POST",
                    "url": "https://httprunner.top/api/v1/Account/Login",
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "json": {
                        "UserName": "test001",
                        "Pwd": "123",
                        "VerCode": ""
                    }
                },
                "validate": [
                    {"check": "status_code", "expect": 200},
                    {"check": "IsSuccess", "expect": true},
                    {"check": "Code", "expect": 200},
                    {"check": "Message", "expect": null}
                ]
            }
        }
    ]


.. _PyPI: https://pypi.python.org/pypi
