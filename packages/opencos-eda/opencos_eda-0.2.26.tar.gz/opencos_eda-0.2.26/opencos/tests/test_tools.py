
# If you want to run this, consider running from the root of opencos repo:
#> python3 -m pytest opencos/*/*.py
# which avoids using any pip installed opencos.eda, and uses the local one
# due to "python3 -m"

import os
import sys
import pytest

from opencos import eda, util, eda_tool_helper


thispath = os.path.dirname(__file__)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()

def test_tools_loaded():
    assert config
    assert len(config.keys()) > 0
    assert len(tools_loaded) > 0

    # Do some very crude checks on the eda.Tool methods, and make
    # sure versions work for Verilator and Vivado:
    if 'verilator' in tools_loaded:
        my_tool = eda.ToolVerilator()
        assert my_tool.get_versions()
        full_ver = my_tool.get_full_tool_and_versions()
        assert 'verilator:' in full_ver
        ver_num = full_ver.split(':')[-1]
        assert float(ver_num)

    if 'vivado' in tools_loaded:
        my_tool = eda.ToolVivado()
        assert my_tool.get_versions()
        full_ver = my_tool.get_full_tool_and_versions()
        assert 'vivado:' in full_ver
        ver_num = full_ver.split(':')[-1]
        assert float(ver_num)

# Run these on simulation tools.
list_of_commands = [
    'sim',
    'elab'
]

list_of_tools = [
    'iverilog',
    'verilator',
    'vivado',
    'modelsim_ase'
]

list_of_deps_targets = [
    ('tb_no_errs', True),       # target:str, sim_expect_pass:bool (sim only, all elab should pass)
    ('tb_dollar_fatal', False),
    ('tb_dollar_err', False),
]

@pytest.mark.parametrize("command", list_of_commands)
@pytest.mark.parametrize("tool", list_of_tools)
@pytest.mark.parametrize("target,sim_expect_pass", list_of_deps_targets)
def test_err_fatal(command, tool, target, sim_expect_pass):
    if tool not in tools_loaded:
        pytest.skip(f"{tool=} skipped, {tools_loaded=}")
        return # skip/pass

    relative_dir = "deps_files/test_err_fatal"
    os.chdir(os.path.join(thispath, relative_dir))
    rc = eda.main(command, '--tool', tool, target)
    print(f'{rc=}')
    if command != 'sim' or sim_expect_pass:
        # command='elab' should pass.
        assert rc == 0
    else:
        assert rc > 0
