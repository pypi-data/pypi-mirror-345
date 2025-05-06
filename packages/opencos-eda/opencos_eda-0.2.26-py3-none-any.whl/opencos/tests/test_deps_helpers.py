
# Get ../eda in our module/package path:
import os
import sys
thispath = os.path.dirname(__file__)
sys.path.append(os.path.join(thispath, '../'))

from opencos import deps_helpers


def test_parse_deps_shell_str__no_parse():
    line = 'some_file.sv'
    d = deps_helpers.parse_deps_shell_str(line, '', '')
    assert d is None, f'{d=}'

    line = 'some_target:'
    d = deps_helpers.parse_deps_shell_str(line, '', '')
    assert d is None, f'{d=}'

    line = '   csr@some_file.sv'
    d = deps_helpers.parse_deps_shell_str(line, '', '')
    assert d is None, f'{d=}'

def test_parse_deps_shell_str__cp():
    line = '    shell@ cp ./oclib_fifo_test.sv oclib_fifo_test_COPY.sv ;'
    d = deps_helpers.parse_deps_shell_str(line, '', '')
    assert d is not None, f'{d=}'
    assert d['exec_list'] == ['cp', './oclib_fifo_test.sv', 'oclib_fifo_test_COPY.sv', ';'], f'{d=}'

def test_parse_deps_shell_str__echo():
    line = '    shell@echo "hello world"'
    d = deps_helpers.parse_deps_shell_str(line, '', '')
    assert d is not None, f'{d=}'
    assert d['exec_list'] == ['echo', '"hello', 'world"'], f'{d=}'

def test_parse_deps_shell_str__path_replacement():
    # Dealing w/ relative paths, change the current working directory to the module directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(module_dir)
    line = 'shell@cp ../deps_helpers.py foo.py'
    d = deps_helpers.parse_deps_shell_str(line, target_path='./', target_node='foo_target')
    assert d is not None, f'{d=}'
    assert d['exec_list'] == ['cp', os.path.abspath('../deps_helpers.py'), 'foo.py'], f'{d=}'
    assert d['target_node'] == 'foo_target'
    assert d['target_path'] == os.path.abspath('./')






def test_parse_deps_work_dir_add_srcs__no_parse():
    line = 'some_file.sv'
    d = deps_helpers.parse_deps_work_dir_add_srcs(line, '', '')
    assert d is None, f'{d=}'

    line = 'some_target:'
    d = deps_helpers.parse_deps_work_dir_add_srcs(line, '', '')
    assert d is None, f'{d=}'

    line = '   csr@some_file.sv'
    d = deps_helpers.parse_deps_work_dir_add_srcs(line, '', '')
    assert d is None, f'{d=}'

def test_parse_deps_work_dir_add_srcs__single_file():
    line = '    work_dir_add_srcs@ single_file.txt'
    d = deps_helpers.parse_deps_work_dir_add_srcs(line, '', '')
    assert d is not None, f'{d=}'
    assert d['file_list'] == ['single_file.txt']

def test_parse_deps_work_dir_add_srcs__several_file():
    line = '    work_dir_add_srcs@ single_file.txt another.sv  gen-verilog/mine.v ./gen-vhdl/wordy.vhdl'
    d = deps_helpers.parse_deps_work_dir_add_srcs(line, '', '')
    assert d is not None, f'{d=}'
    assert d['file_list'] == [
        'single_file.txt', 'another.sv', 'gen-verilog/mine.v', './gen-vhdl/wordy.vhdl'
    ]



def test_parse_deps_peakrdl__no_parse():
    line = 'some_file.sv'
    d = deps_helpers.parse_deps_peakrdl(line, '', '')
    assert d is None, f'{d=}'

    line = 'some_target:'
    d = deps_helpers.parse_deps_peakrdl(line, '', '')
    assert d is None, f'{d=}'

    line = '   csr@some_file.sv'
    d = deps_helpers.parse_deps_peakrdl(line, '', '')
    assert d is None, f'{d=}'

def test_parse_deps_peakrdl__with_top():
    line = '    peakrdl@ --cpuif axi4-lite-flat --top   my_fancy_csrs ./my_csrs.rdl'
    d = deps_helpers.parse_deps_peakrdl(line, '', '')
    assert d is not None, f'{d=}'
    assert len(d['shell_commands_list']) > 0
    assert d['work_dir_add_srcs']['file_list'] == ['peakrdl/my_fancy_csrs_pkg.sv', 'peakrdl/my_fancy_csrs.sv']

def test_parse_deps_peakrdl__with_top2():
    line = '    peakrdl@ --cpuif axi4-lite-flat --top=my_fancy_csrs ./my_csrs.rdl'
    d = deps_helpers.parse_deps_peakrdl(line, '', '')
    assert d is not None, f'{d=}'
    assert len(d['shell_commands_list']) > 0
    assert d['work_dir_add_srcs']['file_list'] == ['peakrdl/my_fancy_csrs_pkg.sv', 'peakrdl/my_fancy_csrs.sv']

def test_parse_deps_peakrdl__infer_top():
    line = '    peakrdl@ --cpuif axi4-lite-flat ./my_csrs.rdl'
    d = deps_helpers.parse_deps_peakrdl(line, '', '')
    assert d is not None, f'{d=}'
    assert len(d['shell_commands_list']) > 0
    assert d['work_dir_add_srcs']['file_list'] == ['peakrdl/my_csrs_pkg.sv', 'peakrdl/my_csrs.sv']
