import argparse
import logging
import os
import sys

from har2case import __version__
from har2case.core import HarParser


def main():
    """ HAR converter: parse command line options and run commands.
    """
    parser = argparse.ArgumentParser(
        description='Convert HAR to YAML/JSON testcases for HttpRunner.')
    parser.add_argument(
        '-V', '--version', dest='version', action='store_true',
        help="show version")
    parser.add_argument('har_source_file', nargs='?',
        help="Specify HAR source file")
    parser.add_argument('output_testset_file', nargs='?',
        help="Optional. Specify converted YAML/JSON testset file.")
    parser.add_argument(
        '--log-level', default='INFO',
        help="Specify logging level, default is INFO.")

    args = parser.parse_args()

    if args.version:
        print("{}".format(__version__))
        exit(0)

    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(level=log_level)

    har_source_file = args.har_source_file
    output_testset_file = args.output_testset_file

    if not har_source_file or not har_source_file.endswith(".har"):
        logging.error("HAR file not specified.")
        sys.exit(1)

    output_file_type = "JSON"
    if not output_testset_file:
        harfile = os.path.splitext(har_source_file)[0]
        output_testset_file = "{}.{}".format(harfile, output_file_type.lower())
    else:
        output_file_suffix = os.path.splitext(output_testset_file)[1]
        if output_file_suffix in [".yml", ".yaml"]:
            output_file_type = "YAML"
        elif output_file_suffix in [".json"]:
            output_file_type = "JSON"
        else:
            logging.error("Converted file could only be in YAML or JSON format.")
            sys.exit(1)

    har_parser = HarParser(har_source_file)

    if output_file_type == "JSON":
        har_parser.gen_json(output_testset_file)
    else:
        har_parser.gen_yaml(output_testset_file)

    return 0
