#!/usr/bin/env python3
# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

"""
Generate a new unit test based on the skeleton
"""


import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Name of the test  to be created")
    parser.add_argument("test_dir",
                        help="Location of the test dir relative to the codechecker repository root. Example: 'analyzer/test/unit'")
    args = parser.parse_args()
    test_name = args.name
    test_dir = args.test_dir

    current_dir = os.path.dirname(os.path.realpath(__file__))
    unit_test_path = os.path.join(current_dir, 'unit')
    test_file_name = 'test_' + test_name + '.py'
    new_test = os.path.join(unit_test_path, test_file_name)
    if os.path.exists(new_test):
        print("Unit test already exists: " + new_test)
        sys.exit(1)

    template = os.path.join(unit_test_path, 'unit_template.py')

    with open(template, 'r', encoding="utf-8", errors="ignore") as init:
        new_test_content = init.read()

    string_to_replace = "$MODULE_NAME$"
    new_test_content = new_test_content.replace(string_to_replace,
                                                test_name)

    print('Generating new test file ...')
    with open(new_test, 'w', encoding="utf-8", errors="ignore") as n_test:
        n_test.write(new_test_content)

    print('Done.')


if __name__ == "__main__":
    main()
