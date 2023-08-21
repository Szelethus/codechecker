# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

import json
import logging
import os

from typing import Dict, List, Optional

from codechecker_report_converter.report import BugPathEvent, File, \
    get_or_create_file, Report

from ..analyzer_result import AnalyzerResultBase


LOG = logging.getLogger('report-converter')

# https://gcc.gnu.org/onlinedocs/gcc-13.2.0/gcc/Diagnostic-Message-Formatting-Options.html
#TODO: Errors, fixits


class AnalyzerResult(AnalyzerResultBase):
    """ Transform analyzer result of the FB Infer. """

    TOOL_NAME = 'gcc'
    NAME = 'GNU GCC'
    URL = 'https://gcc.gnu.org/wiki/StaticAnalyzer'

    def __init__(self):
        super(AnalyzerResult, self).__init__()
        self.__infer_out_parent_dir = None
        self.__file_cache: Dict[str, File] = {}

    def get_reports(self, result_file_path: str) -> List[Report]:
        """ Parse the given analyzer result. """
        reports: List[Report] = []

        if os.path.isdir(result_file_path):
            report_file = os.path.join(result_file_path, "report.json")
            self.__infer_out_parent_dir = os.path.dirname(result_file_path)
        else:
            report_file = result_file_path
            self.__infer_out_parent_dir = os.path.dirname(
                os.path.dirname(result_file_path))

        if not os.path.exists(report_file):
            LOG.error("Report file does not exist: %s", report_file)
            return reports

        try:
            with open(report_file, 'r',
                      encoding="utf-8", errors="ignore") as f:
                bugs = json.load(f)
        except IOError:
            LOG.error("Failed to parse the given analyzer result '%s'. Please "
                      "give an infer output directory which contains a valid "
                      "'report.json' file.", result_file_path)
            return reports

        for bug in bugs:
            report = self.__parse_report(bug)
            if report:
                reports.append(report)

        return reports

    def __get_abs_path(self, source_path):
        """ Returns full path of the given source path.
        It will try to find the given source path relative to the given
        analyzer report directory (infer-out).
        """
        if os.path.exists(source_path):
            return os.path.abspath(source_path)

        full_path = os.path.join(self.__infer_out_parent_dir, source_path)
        if os.path.exists(full_path):
            return full_path

        LOG.warning("No source file found: %s", source_path)

    def __parse_report(self, bug) -> Optional[Report]:
        """ Parse the given report and create a message from them. """

        if 'kind' not in bug:
            return None

        if bug['kind'] != "warning":
            return None

        checker_name = bug['option']
        message = bug['message']

        locations = bug['locations'][0]['caret']
        line = int(locations['line'])
        col = int(locations['column'])
        if col < 0:
            col = 0

        source_path = self.__get_abs_path(locations['file'])
        if not source_path:
            return None

        report = Report(
            file=get_or_create_file(
                os.path.abspath(source_path), self.__file_cache),
            line=line,
            column=col,
            message=message,
            checker_name=checker_name,
            bug_path_events=[],
            notes=[])
        
        if 'path' in bug:
            for bug_trace in bug['path']:
                event = self.__parse_bug_trace(bug_trace)

                if event:
                    report.bug_path_events.append(event)

        for child in bug['children']:
            if child['kind'] == "note":
                event = self.__parse_note(child)

                if event:
                    report.notes.append(event)

        report.bug_path_events.append(BugPathEvent(
            report.message, report.file, report.line, report.column))

        return report

    def __parse_note(self, event) -> Optional[BugPathEvent]:
        locations = event['locations'][0]['caret']
        source_path = self.__get_abs_path(locations['file'])

        return BugPathEvent(
            event['message'],
            get_or_create_file(source_path, self.__file_cache),
            int(locations['line']),
            int(locations['column']))

    def __parse_bug_trace(self, bug_trace) -> Optional[BugPathEvent]:
        """ Creates event from a bug trace element. """

        location = bug_trace['location']
        source_path = self.__get_abs_path(location['file'])
        if not source_path:
            return None

        return BugPathEvent(
            bug_trace['description'],
            get_or_create_file(source_path, self.__file_cache),
            int(location['line']),
            int(location['column']))
