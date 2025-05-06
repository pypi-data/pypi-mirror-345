
import os
import sys
import pytest
import shutil

from opencos import eda, util, eda_tool_helper
from opencos.tests import helpers
from opencos.tests.helpers import eda_wrap, eda_elab_wrap


thispath = os.path.dirname(__file__)

def chdir_remove_work_dir(relpath):
    global thispath
    return helpers.chdir_remove_work_dir(thispath, relpath)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()

# list of tools we'd like to try:
list_of_elab_tools = [
    'slang',
    'verilator',
    'vivado',
    'modelsim_ase',
    'invio',
    'surelog',
    'invio_yosys',
]

list_of_elab_tools_cant_sim = [
    'slang',
    'invio',
    'surelog',
    'invio_yosys',
]

def skip_it(tool):
    return bool( tool not in tools_loaded )

@pytest.mark.parametrize("tool", list_of_elab_tools)
class Tests:

    def test_args_elab(self, tool):
        if skip_it(tool):
            pytest.skip(f"{tool=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        rc = eda_elab_wrap('--tool', tool, 'oclib_priarb')
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_elab(self, tool):
        if skip_it(tool):
            pytest.skip(f"{tool=} skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')
        rc = eda_wrap('multi', 'elab', '--tool', tool, 'oclib_*arb')
        print(f'{rc=}')
        assert rc == 0


@pytest.mark.parametrize("tool", list_of_elab_tools_cant_sim)
class TestsConfirmElab:

    def test_elab_tool_cant_run_sim(self, tool):
        '''Checks eda.check_command_handler_cls(...) so we don't fallback to a different tool'''
        if skip_it(tool):
            pytest.skip(f"{tool=}skipped, {tools_loaded=}")
            return # skip/pass
        chdir_remove_work_dir('../../lib')

        # Calling this will have rc non-zero, but will also throw CommandSim NotImplementedError.
        rc = 0
        try:
            rc = eda_wrap('sim', '--tool', tool, 'oclib_fifo')
        except NotImplementedError:
            rc = 1
        print(f'{rc=}')
        assert rc != 0
