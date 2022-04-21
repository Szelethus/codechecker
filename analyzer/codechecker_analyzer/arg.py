# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------
"""Argument parsing related helper classes and functions."""


import argparse


class OrderedCheckersAction(argparse.Action):
    """
    Action to store enabled and disabled checkers
    and keep ordering from command line.

    Create separate lists based on the checker names for
    each analyzer.
    """

    # Users can supply invocation to 'codechecker-analyze' as follows:
    # -e core -d core.uninitialized -e core.uninitialized.Assign
    # We must support having multiple '-e' and '-d' options and the order
    # specified must be kept when the list of checkers are assembled for Clang.

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(OrderedCheckersAction, self).__init__(option_strings, dest,
                                                    **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):

        if 'ordered_checkers' not in namespace:
            namespace.ordered_checkers = []
        ordered_checkers = namespace.ordered_checkers
        # Map each checker to whether its enabled or not.
        ordered_checkers.append((value, self.dest == 'enable'))

        namespace.ordered_checkers = ordered_checkers


class OrderedAnalyzerConfigAction(argparse.Action):
    """
    TODO
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not '*':
            raise ValueError("nargs must be '*' for backward compatibility "
                             "reasons!")
        super(OrderedAnalyzerConfigAction, self).__init__(option_strings, dest,
                                                          nargs, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):

        if 'analyzer_config' not in namespace:
            namespace.analyzer_config = []
        analyzer_config = namespace.analyzer_config

        assert isinstance(value, list), \
               "--analyzer-config value  (" + str(value) + ") is not a list," \
               " but should be if nargs is not None!"

        analyzer_config.extend(value)

        namespace.analyzer_config = analyzer_config
