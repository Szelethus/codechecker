# coding=utf-8
# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

"""Setup for the test package diff_local_remote_suppress."""


import multiprocessing
import os
import shutil
import sys
import uuid

from libtest import codechecker
from libtest import env
from libtest import project

# Stopping event for CodeChecker server.
__STOP_SERVER = multiprocessing.Event()


def setup_class_common():
    """
    Setup the environment for testing diff_local_remote_suppress.

    Original project
    ------------------------------------------------------
    Checker name            | Severity | Number of reports
    ------------------------------------------------------
    core.CallAndMessage     | HIGH     |                 5
    core.DivideZero         | HIGH     |                10
    core.NullDereference    | HIGH     |                 4
    core.StackAddressEscape | HIGH     |                 3
    cplusplus.NewDelete     | HIGH     |                 5
    deadcode.DeadStores     | LOW      |                 6
    unix.Malloc             | MEDIUM   |                 1
    ------------------------------------------------------

    Project 1
    ------------------------------------------------------
    Checker name            | Severity | Number of reports
    ------------------------------------------------------
    core.CallAndMessage     | HIGH     |                 4 (1 suppressed)
    core.DivideZero         | HIGH     |                10
    core.StackAddressEscape | HIGH     |                 3
    cplusplus.NewDelete     | HIGH     |                 5
    deadcode.DeadStores     | LOW      |                 6
    unix.Malloc             | MEDIUM   |                 1
    ------------------------------------------------------

    Project 2
    ------------------------------------------------------
    Checker name            | Severity | Number of reports
    ------------------------------------------------------
    core.DivideZero         | HIGH     |                 9 (1 suppressed)
    core.NullDereference    | HIGH     |                 4
    core.StackAddressEscape | HIGH     |                 3
    cplusplus.NewDelete     | HIGH     |                 5
    deadcode.DeadStores     | LOW      |                 5 (1 suppressed)
    unix.Malloc             | MEDIUM   |                 1
    ------------------------------------------------------
    """

    os.environ['TEST_WORKSPACE'] = \
        env.get_workspace('diff_local_remote_suppress')
    TEST_WORKSPACE = os.environ['TEST_WORKSPACE']


    # Setup environment variables for the test cases.
    host_port_cfg = {'viewer_host': 'localhost',
                     'viewer_port': env.get_free_port(),
                     'viewer_product': 'diff_local_remote_suppress'}
    # Config options.
    codechecker_cfg = {
        'suppress_file': None,
        'skip_list_file': None,
        'check_env': env.test_env(TEST_WORKSPACE),
        'workspace': TEST_WORKSPACE,
        'checkers': [],
        'analyzers': ['clangsa'],
        'run_names': {}
    }

    codechecker_cfg.update(host_port_cfg)

    # Start or connect to the running CodeChecker server and get connection
    # details.
    print("This test uses a CodeChecker server... connecting...")
    codechecker.start_server(codechecker_cfg, __STOP_SERVER)

    codechecker.add_test_package_product(
        host_port_cfg, os.environ['TEST_WORKSPACE'])

    TEST_WORKSPACE = os.environ['TEST_WORKSPACE']

    test_project = 'cpp'

    project_info = project.get_info(test_project)

    test_config = {}
    test_config['test_project'] = project_info
    test_config['codechecker_cfg'] = codechecker_cfg

    env.export_test_cfg(TEST_WORKSPACE, test_config)
    cc_client = env.setup_viewer_client(TEST_WORKSPACE)
    for run_data in cc_client.getRunData(None, None, 0, None):
        cc_client.removeRun(run_data.runId, None)

    # Copy "cpp" test project 3 times to different directories.

    test_proj_path_orig = os.path.join(TEST_WORKSPACE, "test_proj_orig")
    test_proj_path_1 = os.path.join(TEST_WORKSPACE, "test_proj_1")
    test_proj_path_2 = os.path.join(TEST_WORKSPACE, "test_proj_2")

    shutil.rmtree(test_proj_path_orig, ignore_errors=True)
    shutil.rmtree(test_proj_path_1, ignore_errors=True)
    shutil.rmtree(test_proj_path_2, ignore_errors=True)
    shutil.copytree(project.path(test_project), test_proj_path_orig)
    shutil.copytree(project.path(test_project), test_proj_path_1)
    shutil.copytree(project.path(test_project), test_proj_path_2)

    project_info['project_path_orig'] = test_proj_path_orig
    project_info['project_path_1'] = test_proj_path_1
    project_info['project_path_2'] = test_proj_path_2

    # Log, analyze and store original project.
    # No changes in the project.

    codechecker_cfg['workspace'] = test_proj_path_orig
    codechecker_cfg['reportdir'] = os.path.join(test_proj_path_orig, 'reports')

    ret = codechecker.log_and_analyze(codechecker_cfg, test_proj_path_orig)
    if ret:
        sys.exit(1)

    run_name_project_orig = project_info['name'] + '_' + uuid.uuid4().hex
    codechecker_cfg['run_names']['test_project_orig'] = run_name_project_orig
    ret = codechecker.store(codechecker_cfg, run_name_project_orig)
    if ret:
        sys.exit(1)

    # Log, analyze and store project 1.
    # Modifications:
    #   - Suppress a core.CallAndMessage report.
    #   - Options: "-e core.CallAndMessage -d core.NullDereference"

    project.insert_suppression(
        os.path.join(test_proj_path_1, "call_and_message.cpp"))

    codechecker_cfg['workspace'] = test_proj_path_1
    codechecker_cfg['reportdir'] = os.path.join(test_proj_path_1, 'reports')
    codechecker_cfg['checkers'] = [
        '-e', 'core.CallAndMessage', '-d', 'core.NullDereference']

    ret = codechecker.log_and_analyze(codechecker_cfg, test_proj_path_1)
    if ret:
        sys.exit(1)

    run_name_project_1 = project_info['name'] + '_' + uuid.uuid4().hex
    codechecker_cfg['run_names']['test_project_1'] = run_name_project_1
    ret = codechecker.store(codechecker_cfg, run_name_project_1)
    if ret:
        sys.exit(1)

    # Log, analyze and store project 2.
    # Modifications:
    #   - Suppress a core.DivideZero report.
    #   - Options: "-d core.CallAndMessage -e core.NullDereference"

    project.insert_suppression(
        os.path.join(test_proj_path_2, "divide_zero.cpp"))

    codechecker_cfg['workspace'] = test_proj_path_2
    codechecker_cfg['reportdir'] = os.path.join(test_proj_path_2, 'reports')
    codechecker_cfg['checkers'] = [
        '-d', 'core.CallAndMessage', '-e', 'core.NullDereference']

    ret = codechecker.log_and_analyze(codechecker_cfg, test_proj_path_2)
    if ret:
        sys.exit(1)

    run_name_project_2 = project_info['name'] + '_' + uuid.uuid4().hex
    codechecker_cfg['run_names']['test_project_2'] = run_name_project_2
    ret = codechecker.store(codechecker_cfg, run_name_project_2)
    if ret:
        sys.exit(1)

    # Export the test configuration to the workspace.
    env.export_test_cfg(TEST_WORKSPACE, test_config)


def teardown_class_common():
    TEST_WORKSPACE = os.environ['TEST_WORKSPACE']

    # Removing the product through this server requires credentials.
    codechecker_cfg = env.import_test_cfg(TEST_WORKSPACE)['codechecker_cfg']
    codechecker.remove_test_package_product(TEST_WORKSPACE,
                                            codechecker_cfg['check_env'])

    __STOP_SERVER.set()
    __STOP_SERVER.clear()

    print("Removing: " + TEST_WORKSPACE)
    shutil.rmtree(TEST_WORKSPACE, ignore_errors=True)
