
# If you want to run this, consider running from the root of opencos repo:
#> python3 -m pytest --verbose opencos/*/*.py
#> python3 -m pytest -rx opencos/*/*.py
# which avoids using any pip installed opencos.eda, and uses the local one
# due to "python3 -m"

import os
import sys
import pytest
import shutil

from opencos import eda, util, eda_tool_helper
from opencos.tests import helpers
from opencos.tests.helpers import eda_wrap, eda_sim_wrap, eda_elab_wrap, \
    assert_sim_log_passes, assert_gen_deps_yml_good, assert_export_json_good, \
    assert_export_jsonl_good, Helpers


thispath = os.path.dirname(__file__)

def chdir_remove_work_dir(relpath):
    global thispath
    return helpers.chdir_remove_work_dir(thispath, relpath)

# Figure out what tools the system has available, without calling eda.main(..)
config, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()


class TestsEdaHelp(Helpers):
    def test_args_help(self):
        rc = self.log_it('help', use_eda_wrap=False)
        print(f'{rc=}')
        assert rc == 0
        assert self.is_in_log('<command> [options] <files|targets, ...>')
        assert self.is_in_log('"eda help sim" for specific help')
        # Some things we should not see:
        assert not self.is_in_log("sim-plusargs")
        assert not self.is_in_log("waves-start")

    def test_args_help_sim(self):
        rc = self.log_it('help sim', use_eda_wrap=False)
        print(f'{rc=}')
        assert rc == 0
        assert self.is_in_log("Generic help for command='sim'")
        # Look for some unique args:
        assert self.is_in_log("sim-plusargs")
        assert self.is_in_log("waves-start")
        # Some things we should not see:
        assert not self.is_in_log('Usage: eda <command> <options> <targets>')
        assert not self.is_in_log('"eda help sim" for specific help')


    def test_args_debug(self):
        # we'll lose coverage on this, but for interactive mode it looks like
        # monkeypatch isn't an option. We'll use subprocess.run:
        #  ../../bin/eda
        # Doing this, we also lose the debug of: pytest -rP --verbose (test-path)
        # to show us the actual results to stdout.
        import subprocess
        res = subprocess.run(
            [ os.path.join(thispath, '..', '..', 'bin', 'eda'), '--debug' ],
            input = b'exit\n\n',
            capture_output=True,
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''


def test_args_sim_default_tool():
    chdir_remove_work_dir('../../lib/tests')
    rc = eda_sim_wrap('oclib_fifo_test')
    print(f'{rc=}')
    assert rc == 0

def test_export_peakrdl_eth10gcsrs():
    '''Confirm eda export works for CSRs.'''
    chdir_remove_work_dir('../../top')
    outdir = os.path.join(os.getcwd(), 'eda.export')
    if os.path.exists(outdir):
        os.remove(outdir)
    rc = eda_wrap('export', 'oc_eth_10g_csrs')
    assert rc == 0
    # confirm outputs:
    deps_yml_path = os.path.join(os.getcwd(), 'eda.export', 'oc_eth_10g_csrs.export', 'DEPS.yml')
    assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oc_eth_10g_csrs')

def test_multi_export__lib_oclib_csr():
    chdir_remove_work_dir('../../lib')
    outdir = os.path.join(os.getcwd(), 'eda.export')
    if os.path.exists(outdir):
        os.remove(outdir)
    rc = eda.main('multi', 'export', '--fail-if-no-targets', '"oclib_csr*"')
    print(f'{rc=}')
    assert rc == 0
    # confirm one output:
    deps_yml_path = os.path.join(os.getcwd(), 'eda.export', 'oclib_csr_adapter.export', 'DEPS.yml')
    assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oclib_csr_adapter')

def test_multi_export__lib_tests_fifos():
    chdir_remove_work_dir('../../lib/tests')
    outdir = os.path.join(os.getcwd(), 'eda.export')
    if os.path.exists(outdir):
        os.remove(outdir)
    rc = eda.main('multi', 'export', '--fail-if-no-targets', '"oclib_fifo_test"')
    print(f'{rc=}')
    assert rc == 0
    # confirm one output:
    deps_yml_path = os.path.join(os.getcwd(), 'eda.export', 'oclib_fifo_test.export', 'DEPS.yml')
    assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oclib_fifo_test')


@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestsRequiresVerilator(Helpers):
    def test_verilator_cant_run_synth(self):
        '''Checks eda.check_command_handler_cls(...) so we don't fallback to a different tool'''
        # If you say you want verilator, then we will NOT choose a different default handler.
        chdir_remove_work_dir('../../lib')
        rc = eda_wrap('synth', '--tool', 'verilator', 'oclib_fifo')
        print(f'{rc=}')
        assert rc != 0


    def test_args_sim(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0


    def test_args_sim_tool_with_path(self):
        import shutil
        verilator_fullpath = shutil.which('verilator')
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', f'verilator={verilator_fullpath}', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_sim_with_coverage(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_wrap('sim', '--coverage', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0
        # We don't check the logs, but the command should succeed.

    def test_args_lint_only_sim(self):
        '''Confirm --lint-only works for Verilator with 'sim' command.'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--lint-only', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_elab(self):
        chdir_remove_work_dir('../../lib')
        rc = eda_elab_wrap('--tool', 'verilator', 'oclib_priarb')
        print(f'{rc=}')
        assert rc == 0

    def test_args_export_sim(self):
        '''Confirm --export works for Verilator with 'sim' command.'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--export', '--tool', 'verilator', 'oclib_rrarb_test')
        print(f'{rc=}')
        assert rc == 0
        # Confirm that we have an exported DEPS.yml in the correct directory and the DEPS.yml
        # is loadable.
        deps_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_rrarb_test.sim', 'export', 'DEPS.yml')
        assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oclib_rrarb_test')

    def test_args_export_run_sim(self):
        '''Confirm --export-run works for Verilator with 'sim' command.'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--export-run', '--tool', 'verilator', 'oclib_priarb_test')
        print(f'{rc=}')
        assert rc == 0
        # Confirm that we have an exported DEPS.yml in the correct directory and the DEPS.yml
        # is loadable.
        deps_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_priarb_test.sim', 'export', 'DEPS.yml')
        assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oclib_priarb_test')
        # Confirm that we ran the test via --export-run
        sim_out_export_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_priarb_test.sim', 'export',
                                           'eda.work', 'oclib_priarb_test.sim', 'sim.log')
        assert_sim_log_passes(sim_out_export_path)

    def test_args_export_export_json(self):
        '''Confirm --export-json works for Verilator with 'sim' command.'''
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--export-json', '--tool', 'verilator', 'oclib_axist_tfirst_test')
        print(f'{rc=}')
        assert rc == 0
        # Confirm that we have an exported DEPS.yml in the correct directory and the DEPS.yml
        # is loadable.
        deps_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_axist_tfirst_test.sim', 'export', 'DEPS.yml')
        assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oclib_axist_tfirst_test')
        # Confirm that we have a export.json in the expected directory
        export_json_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_axist_tfirst_test.sim', 'export', 'export.json')
        assert_export_json_good(export_json_path)

    def test_elab_export_run_peakrdl_eth10gcsrs(self):
        '''Confirm eda, elab -export-run works for elab (verilator).'''
        chdir_remove_work_dir('../../top')
        rc = eda_elab_wrap('--export-run', '--tool', 'verilator', '--top', 'oc_eth_10g_1port_csrs', 'oc_eth_10g_csrs')
        assert rc == 0
        # confirm outputs:
        deps_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oc_eth_10g_csrs.elab', 'export', 'DEPS.yml')
        assert_gen_deps_yml_good(filepath=deps_yml_path, want_target='oc_eth_10g_csrs')
        # Confirm that we ran the test via --export-run
        elab_out_export_path = os.path.join(os.getcwd(), 'eda.work', 'oc_eth_10g_csrs.elab', 'export',
                                            'eda.work', 'oc_eth_10g_csrs.elab', 'compile.log')
        assert_sim_log_passes(elab_out_export_path, want_str='V e r i l a t i o n   R e p o r t:')



    def test_run_from_work_dir(self):
        '''
        Uses eda --stop-before-compile to craft the eda.work/(test)/ dirs and shell commands,
        and confirms that we can run those shell commands.
        '''

        import subprocess
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--stop-before-compile', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

        os.chdir(os.path.join(thispath, '../../lib/tests/eda.work/oclib_fifo_test.sim'))
        res = subprocess.run(
            [ './lint_only.sh' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''

        res = subprocess.run(
            [ './all.sh' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''

        res = subprocess.run(
            [ './simulate_only.sh' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        rc = res.returncode
        print(f'{rc=}')
        assert rc == 0
        assert res.stdout
        assert res.stderr == b''

    def test_args_sim_waves(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', 'verilator', '--waves', 'oclib_fifo_test')
        print(f'{rc=}')
        assert os.path.exists(os.path.join('.', 'eda.work', 'oclib_fifo_test.sim', 'dump.fst'))
        assert rc == 0

    def test_args_sim_waves_dumpvcd(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--tool', 'verilator', '--waves', '--dump-vcd', 'oclib_fifo_test')
        print(f'{rc=}')
        assert os.path.exists(os.path.join('.', 'eda.work', 'oclib_fifo_test.sim', 'dump.vcd'))
        assert rc == 0

    def test_args_sim_dumpvcd_verilator_trace(self):
        '''Do not set --dump-vcd, set --waves and do directly set +trace=vcd, and confirm +trace works as a bare CLI plusarg'''
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator --waves +trace=vcd oclib_fifo_test')
        assert rc == 0
        assert os.path.exists(os.path.join('.', 'eda.work', 'oclib_fifo_test.sim', 'dump.vcd'))
        lines = self.get_log_lines_with('exec: ./obj_dir/sim.exe')
        assert len(lines) == 1
        assert ' +trace=vcd ' in lines[0]
        assert ' +trace ' not in lines[0]

    def test_args_seed1(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator --seed=1 oclib_fifo_test')
        assert rc == 0
        lines = self.get_log_lines_with('exec: ./obj_dir/sim.exe')
        assert len(lines) == 1
        assert ' +verilator+seed+1 ' in lines[0]

    def test_args_WnoFatal(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator --verilate-args=-Wno-fatal oclib_fifo_test')
        assert rc == 0
        lines = self.get_log_lines_with('exec: ')
        assert len(lines) == 2
        assert 'verilator' in lines[0]
        assert ' -Wno-fatal ' in lines[0]
        assert 'sim.exe' in lines[1]

    def test_args_sim_should_fail(self):
        chdir_remove_work_dir('../../lib/tests')
        # We'd expect this to fail b/c --xilinx and --tool verilator flags an error. I do not
        # want to use the xfail pytest decorator.
        rc = eda_sim_wrap('--xilinx', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc != 0

    def test_more_plusargs_sim(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = self.log_it('sim --tool verilator +info=300 +some_plusarg_novalue oclib_fifo_test')
        assert rc == 0
        lines = self.get_log_lines_with('exec: ./obj_dir/sim.exe')
        assert len(lines) == 1
        assert ' +info=300 ' in lines[0]
        assert ' +info ' not in lines[0]
        assert ' +some_plusarg_novalue ' in lines[0]
        assert ' +some_plusarg_novalue=' not in lines[0]

    def test_args_multi_sim(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_sim_timeout(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--tool', 'verilator', '--single-timeout', '10',
                      'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_args_multi_sim_should_fail(self):
        chdir_remove_work_dir('../../lib/tests')
        # We'd expect this to fail b/c --xilinx and --tool verilator flags an error. I do not
        # want to use the xfail pytest decorator.
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--xilinx', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc != 0

    def test_args_multi_sim_no_targets_should_fail(self):
        chdir_remove_work_dir('../../lib/tests')
        # We'd expect this to fail b/c no_targets* should expand to nothing.
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--seed=1', '--tool', 'verilator', 'no_targets*')
        print(f'{rc=}')
        assert rc != 0

    def test_multi_sim_export_jsonl(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--export-jsonl', '--tool', 'verilator', '*test')
        print(f'{rc=}')
        assert rc == 0
        # Confirm that we have a export.jsonl in the expected directory
        export_json_path = os.path.join(os.getcwd(), 'eda.work', 'export', 'export.jsonl')
        assert_export_jsonl_good(export_json_path, jsonl=True)

    def test_multi_sim_export_single_json(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda.main('multi', 'sim', '--fail-if-no-targets', '--export-json', '--tool', 'verilator', '*test')
        print(f'{rc=}')
        assert rc == 0
        # Confirm that we have a export.json in the expected directory
        export_json_path = os.path.join(os.getcwd(), 'eda.work', 'export', 'export.json')
        assert_export_jsonl_good(export_json_path, jsonl=False)

    def test_elab_verilator_no_deps_files_involved(self):
        # no --top set, have to infer its final file name.
        chdir_remove_work_dir('../../lib')
        cmd_list = 'elab --tool verilator +incdir+.. oclib_assert_pkg.sv oclib_pkg.sv'.split()
        cmd_list += '../sim/ocsim_pkg.sv ../sim/ocsim_urand.sv ./rams/oclib_ram1r1w_infer.sv'.split()
        cmd_list += './rams/oclib_ram1r1w_infer_core.v oclib_fifo.sv'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc == 0
        # We don't get a log for this, but we can check the output generated eda_output_config.yml.
        eda_config_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_fifo.elab', 'eda_output_config.yml')
        data = util.yaml_safe_load(eda_config_yml_path)
        assert 'args' in data
        assert data['args'].get('top', '') == 'oclib_fifo'
        assert 'config' in data
        assert 'eda_original_args' in data['config']
        assert 'oclib_fifo.sv' in data['config']['eda_original_args']
        assert data.get('target', '') == 'oclib_fifo'

    def test_elab_verilator_some_deps_files_involved(self):
        # no --top set, have to infer its final file name.
        chdir_remove_work_dir('../../lib')
        cmd_list = 'elab --tool verilator +incdir+.. all_pkg oclib_ram1r1w oclib_fifo.sv'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc == 0
        # We don't get a log for this, but we can check the output generated eda_output_config.yml.
        eda_config_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_fifo.elab', 'eda_output_config.yml')
        data = util.yaml_safe_load(eda_config_yml_path)
        assert 'args' in data
        assert data['args'].get('top', '') == 'oclib_fifo'
        assert 'config' in data
        assert 'eda_original_args' in data['config']
        assert 'oclib_fifo.sv' in data['config']['eda_original_args']
        assert 'all_pkg' in data['config']['eda_original_args']
        assert 'oclib_ram1r1w' in data['config']['eda_original_args']
        assert data.get('target', '') == 'oclib_fifo'

    def test_elab_verilator_no_deps_files_involved_should_fail(self):
        chdir_remove_work_dir('../../lib')
        # pick some non-existent file oclib_doesnt_exist.nope.sv
        cmd_list = 'elab --tool verilator +incdir+.. oclib_doesnt_exist.nope.sv'.split()
        cmd_list +=' oclib_assert_pkg.sv oclib_pkg.sv oclib_fifo.sv'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc != 0

    def test_config_reduced_yml(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--config-yml', 'eda_config_reduced.yml', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_config_max_verilator_waivers_yml(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--config-yml', 'eda_config_max_verilator_waivers.yml', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0

    def test_config_yml_custom(self):
        chdir_remove_work_dir('../../lib/tests')
        rc = eda_sim_wrap('--config-yml', '../../opencos/tests/custom_config.yml', '--tool', 'verilator', 'oclib_fifo_test')
        print(f'{rc=}')
        assert rc == 0
        eda_config_yml_path = os.path.join(os.getcwd(), 'eda.work', 'oclib_fifo_test.sim', 'eda_output_config.yml')
        data = util.yaml_safe_load(eda_config_yml_path)
        # make sure this config was actually used. We no longer re-add it to args
        # (it won't show up in 'original_args') it will will show up in the config though:
        used_yml_fname = data['config']['config-yml']
        assert used_yml_fname.endswith('opencos/tests/custom_config.yml')
        # this config overrides a value to False:
        assert 'config' in data
        config = data['config']
        assert config['dep_command_enables']['shell'] is False


class TestMissingDepsFileErrorMessages(Helpers):
    DEFAULT_DIR = os.path.join(thispath, 'deps_files', 'no_deps_here', 'empty')
    DEFAULT_LOG = 'eda.log'

    def test_bad0(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad0')
        assert rc != 0
        assert self.is_in_log(
            'Trying to resolve command-line target=./target_bad0: was not found',
            'in deps_file=None, possible targets in deps file = []'
        )


class TestDepsResolveErrorMessages(Helpers):
    DEFAULT_DIR = os.path.join(thispath, 'deps_files', 'error_msgs')
    DEFAULT_LOG = 'eda.log'

    # files foo.sv, foo2.sv, target_bad0.sv, and target_bad1.sv exist.
    # files missing*.sv and targets missing* do not exist.
    # These all run elab targets.

    def test_good0(self):
        self.chdir()
        rc = self.log_it('elab foo')
        assert rc == 0

    def test_good1(self):
        self.chdir()
        rc = self.log_it('elab foo2')
        assert rc == 0

    def test_good2(self):
        self.chdir()
        rc = self.log_it('elab target_good2')
        assert rc == 0

    def test_good3(self):
        self.chdir()
        rc = self.log_it('elab target_good3')
        assert rc == 0

    # Bit of a change-detector-test here, but I want to make sure the
    # line= numbers get reported correctly for the calling target.
    def test_bad0(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad0')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing0.sv (file?): called from ./DEPS.yml::target_bad0::line=20,",
            "File=missing0.sv not found in directory=."
        )

    def test_bad1(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad1')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing1.sv (file?): called from ./DEPS.yml::target_bad1::line=24,",
            "File=missing1.sv not found in directory=."
        )

    def test_bad2(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad2')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing2.sv (file?): called from ./DEPS.yml::target_bad2::line=28,",
            "File=missing2.sv not found in directory=."
        )

    def test_bad3(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad3')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing3.sv (file?): called from ./DEPS.yml::target_bad3::line=33,",
            "File=missing3.sv not found in directory=."
        )

    def test_bad4(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad4')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing_target4: called from ./DEPS.yml::target_bad4::line=39,",
            "Target not found in deps_file=./DEPS.yml"
        )

    def test_bad5(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad5')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing_target5: called from ./DEPS.yml::target_bad5::line=43,",
            "Target not found in deps_file=./DEPS.yml"
        )

    def test_bad6(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad6')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing_target6: called from ./DEPS.yml::target_bad6::line=47,",
            "Target not found in deps_file=./DEPS.yml"
        )

    def test_bad7(self):
        self.chdir()
        rc = self.log_it(command_str='elab target_bad7')
        assert rc != 0
        assert self.is_in_log(
            "target=./missing_target7: called from ./DEPS.yml::target_bad7::line=52,",
            "Target not found in deps_file=./DEPS.yml"
        )

    def test_cmd_line_good0(self):
        self.chdir()
        rc = self.log_it(command_str='elab foo.sv')
        assert rc == 0

    def test_cmd_line_good1(self):
        self.chdir()
        rc = self.log_it(command_str='elab foo.sv foo2.sv')
        assert rc == 0

    def test_cmd_line_bad0(self):
        self.chdir()
        rc = self.log_it(command_str='elab nope_target0')
        assert rc != 0
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_target0: was not",
            "found in deps_file=./DEPS.yml, possible targets in deps file = ['foo'"
        )

    def test_cmd_line_bad1(self):
        self.chdir()
        rc = self.log_it(command_str='elab foo.sv nope_target1')
        assert rc != 0
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_target1: was not",
            "found in deps_file=./DEPS.yml, possible targets in deps file = ['foo'"
        )

    def test_cmd_line_bad2(self):
        self.chdir()
        rc = self.log_it(command_str='elab nope_file0.sv')
        assert rc != 0
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_file0.sv",
            "(file?): File=nope_file0.sv not found in directory=."
        )

    def test_cmd_line_bad3(self):
        self.chdir()
        rc = self.log_it(command_str='elab foo2.sv nope_file1.sv')
        assert rc != 0
        assert self.is_in_log(
            "Trying to resolve command-line target=./nope_file1.sv",
            "(file?): File=nope_file1.sv not found in directory=."
        )




@pytest.mark.skipif('iverilog' not in tools_loaded, reason="requires iverilog")
class TestsRequiresIVerilog:
    def test_iverilog(self):
        chdir_remove_work_dir('deps_files/iverilog_test')
        cmd_list = 'sim --tool iverilog target_test'.split()
        rc = eda.main(*cmd_list)
        print(f'{rc=}')
        assert rc == 0

class TestDepsReqs:
    def test_deps_reqs(self):
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs2(self):
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test2'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs3(self):
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test3'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs4(self):
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim foo_test4'.split()
        rc = eda.main(*cmd_list)
        assert rc == 0

    def test_deps_reqs5(self):
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim should_fail_foo_test5'.split()
        rc = eda.main(*cmd_list)
        assert rc != 0

    def test_deps_reqs6(self):
        chdir_remove_work_dir('deps_files/non_sv_reqs')
        cmd_list = 'sim should_fail_foo_test6'.split()
        rc = eda.main(*cmd_list)
        assert rc != 0


def test_deps_command_order():
    from contextlib import redirect_stdout, redirect_stderr
    chdir_remove_work_dir('deps_files/command_order')
    cmd_list = 'sim --stop-before-compile target_test'.split()
    with open('eda.log', 'w') as f:
        with redirect_stdout(f):
            with redirect_stderr(f):
                rc = eda.main(*cmd_list)

    print(f'{rc=}')
    assert rc == 0

    # We should see "hi" before "bye" to confirm deps + command order is correct.
    # see ./deps_files/command_order/DEPS.yml - target = target_test
    found_str_list = [
        'exec: echo "hi"',
        'exec: echo "bye"',
    ]
    found_lines_list = [None, None]

    with open('eda.log') as f:
        for iter,line in enumerate(f.readlines()):
            line = line.rstrip()
            for idx,key in enumerate(found_str_list):
                if key in line:
                    found_lines_list[idx] = iter

    assert found_lines_list[0] # found hi
    assert found_lines_list[1] # found bye
    assert found_lines_list[0] < found_lines_list[1] # hi before bye

    # Added check, we redirected to create eda.log earlier to confirm the targets worked,
    # but as a general eda.py check, all shell commands should create their own {target}__shell_0.log file:
    work_dir = os.path.join(thispath, 'deps_files/command_order', 'eda.work', 'target_test.sim')
    with open(os.path.join(work_dir, 'target_echo_hi__shell_0.log')) as f:
        text = ''.join(f.readlines()).strip()
        assert text == 'hi'
    # Added check, one of the targets uses a custom 'tee' file name, instead of the default log.
    with open(os.path.join(work_dir, 'custom_tee_echo_bye.log')) as f:
        text = ''.join(f.readlines()).strip()
        assert text == 'bye'


@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestDepsOtherMarkup:

    def test_deps_toml(self):
        chdir_remove_work_dir('./deps_files/test_deps_toml')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

    def test_deps_json(self):
        chdir_remove_work_dir('./deps_files/test_deps_json')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

    def test_deps_no_extension(self):
        chdir_remove_work_dir('./deps_files/test_deps_noext')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_test')
        print(f'{rc=}')
        assert rc == 0

@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestForceFileExt(Helpers):
    def test_sv_at(self):
        chdir_remove_work_dir('./deps_files/force_file_ext')
        rc = self.log_it('sim --tool verilator sv@foo.txt')
        assert rc == 0
        assert self.is_in_log("force_file_ext/foo.txt:6: Verilog $finish")


@pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
class TestDepsNoFilesTargets(Helpers):

    def test_eda_sim__use_implicit_one_target(self):
        '''This test should work if the DEPS markup has a single target only'''
        # Using this b/c DEPS.toml has single target.
        chdir_remove_work_dir('./deps_files/test_deps_toml')
        rc = self.log_it('sim --tool verilator')
        assert rc == 0
        # Confirm the 'target_test' was used.
        assert self.is_in_log("using 'target_test' from")
        exec_lines = self.get_log_lines_with('exec: ')
        assert 'verilator ' in exec_lines[0]
        assert self.is_in_log("test_deps_toml/foo.sv:6: Verilog $finish")

    def test_eda_sim__wrong_target_shouldfail(self):
        '''This test should fail, wrong target name'''
        # Using this b/c DEPS.toml has single target.
        chdir_remove_work_dir('./deps_files/test_deps_toml')
        rc = eda_wrap('sim', '--tool', 'verilator', 'target_whoops')
        assert rc == 1

    def test_eda_sim__no_files_or_targets_shouldfail(self):
        '''This test should fail, there is DEPS.yml (empty, no implicit target), or missing file'''
        chdir_remove_work_dir('./deps_files/no_deps_here')
        rc = eda_wrap('sim', '--tool', 'verilator')
        assert rc == 1

    def test_eda_sim__no_files_or_targets_with_top_shouldfail(self):
        '''This test should fail, there is DEPS.yml (empty, no implicit target), or missing file'''
        chdir_remove_work_dir('./deps_files/no_deps_here')
        rc = eda_wrap('sim', '--tool', 'verilator', '--top', 'empty_file')
        assert rc == 1


class TestDepsTags(Helpers):
    DEFAULT_DIR = os.path.join(thispath, 'deps_files', 'tags_with_tools')
    DEFAULT_LOG = 'eda.log'

    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_verilator(self):
        self.chdir()
        logfile = 'verilator_eda.log'
        rc = self.log_it('sim --tool verilator target_test', logfile=logfile)
        assert rc == 0

        # so the full sim should have not run
        exec_lines = self.get_log_lines_with('exec: ', logfile=logfile)
        assert len(exec_lines) == 1, \
            f'{exec_lines=} should have only been the compile --lint-only'
        assert 'exec: ' in exec_lines[0] and 'verilator ' in exec_lines[0], \
            f'{exec_lines[0]=} should have been verilator compile'


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_replace_config_tools_verilator(self):
        self.chdir()
        logfile = 'target_with_replace_config_tools_test.log'
        rc = self.log_it('sim --tool verilator target_with_replace_config_tools_test',
                         logfile=logfile)
        assert rc == 0
        # This target overrode all the Verilator waivers to nothing, so
        # we should see zero -Wno- in the log for verilator exec lines.
        exec_lines = self.get_log_lines_with('exec: ', logfile=logfile)
        assert len(exec_lines) == 2
        assert not '-Wno-' in exec_lines[0], f'{line=}'


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_additive_config_tools_verilator(self):
        self.chdir()
        logfile = 'target_with_additive_config_tools_test.log'
        rc = self.log_it('sim --tool verilator --debug target_with_additive_config_tools_test',
                         logfile=logfile)
        assert rc == 0
        # This target added to the Verilator waivers -Wno-style, -Wno-fatal,
        # but the defaults should also be there (at least -Wno-UNSIGNED)
        waivers = self.get_log_words_with('-Wno-', logfile=logfile)
        assert '-Wno-style' in waivers
        assert '-Wno-fatal' in waivers
        assert '-Wno-UNSIGNED' in waivers


    @pytest.mark.skipif('vivado' not in tools_loaded, reason="requires vivado")
    def test_tags_with_tools_vivado(self):
        self.chdir()
        logfile = 'vivado_eda.log'
        rc = self.log_it('sim --tool vivado target_test', logfile=logfile)
        assert rc == 0

        # make sure the tag wasn't applied (should only be applied in verilator)
        # so the full sim should have run (xvlog, xelab, xsim) (--lint-only not applied,
        # b/c that should only apply in 'verilator' for this target.)
        exec_lines = self.get_log_lines_with('exec: ', logfile=logfile)
        assert len(exec_lines) == 3
        assert 'xvlog ' in exec_lines[0]
        assert 'xelab ' in exec_lines[1]
        assert 'xsim ' in exec_lines[2]
        assert not self.is_in_log('--lint-only', logfile=logfile)


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_add_incdirs(self):
        self.chdir()
        logfile = 'target_foo_sv_add_incdirs.log'
        rc = self.log_it('elab --tool verilator target_foo_sv_add_incdirs',
                         logfile=logfile)
        assert rc == 0
        # This target added . to incdirs in the DEPS.yml dir.

        incdirs = self.get_log_words_with('+incdir+', logfile=logfile)
        assert len(incdirs) == 1 # should only have 1
        assert 'tests/deps_files/tags_with_tools' in incdirs[0]


    @pytest.mark.skipif('verilator' not in tools_loaded, reason="requires verilator")
    def test_tags_with_tools_add_defines(self):
        self.chdir()
        logfile = 'target_foo_sv_add_defines.log'
        rc = self.log_it('elab --tool verilator --debug target_foo_sv_add_defines',
                         logfile=logfile)
        assert rc == 0
        assert self.is_in_log('+define+FOO_SV=3000', logfile=logfile)
