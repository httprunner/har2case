""" Convert HAR (HTTP Archive) to YAML/JSON testcase for HttpRunner.

Usage:
    # convert to JSON format testcase
    >>> har2case demo.har

    # convert to YAML format testcase
    >>> har2case demo.har -2y

"""

import argparse
import logging
import sys

from har2case.__about__ import __description__, __version__
from har2case.core import HarParser


def main():
    """ HAR converter: parse command line options and run commands.
    """
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        '-V', '--version', dest='version', action='store_true',
        help="show version")
    parser.add_argument(
        '--log-level', default='INFO',
        help="Specify logging level, default is INFO.")
    parser.add_argument('har_source_file', nargs='?',
        help="Specify HAR source file")
    parser.add_argument(
        '-2y', '--to-yml', '--to-yaml',
        dest='to_yaml', action='store_true',
        help="Convert to YAML format, if not specified, convert to JSON format by default.")
    parser.add_argument(
        '--filter', help="Specify filter keyword, only url include filter string will be converted.")
    parser.add_argument(
        '--exclude',
        help="Specify exclude keyword, url that includes exclude string will be ignored, multiple keywords can be joined with '|'")

    args = parser.parse_args()

    if args.version:
        print("{}".format(__version__))
        exit(0)

    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(level=log_level)

    har_source_file = args.har_source_file
    if not har_source_file or not har_source_file.endswith(".har"):
        logging.error("HAR file not specified.")
        sys.exit(1)

    output_file_type = "YAML" if args.to_yaml else "JSON"
    HarParser(
        har_source_file, args.filter, args.exclude
    ).gen_testcase(output_file_type)

    return 0
