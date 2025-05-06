
import os
import sys
import shutil

from opencos import eda, util
from opencos import deps_schema

def chdir_remove_work_dir(startpath, relpath):
    os.chdir(os.path.join(startpath, relpath))
    for outdir in ['eda.export', 'eda.work']:
        fullp = os.path.join(os.getcwd(), outdir)
        if fullp and ('eda.' in fullp) and os.path.isdir(fullp):
            shutil.rmtree(fullp)

def eda_wrap(*args):
    '''Calls eda.main, prefer use seed=1 to avoid seed based simulation fails in pytests'''
    main_args = [x for x in list(args) if ('--seed' not in x)]
    return eda.main('--seed=1', *main_args)

def eda_sim_wrap(*args):
    '''Calls eda.main, prefer use seed=1 to avoid seed based simulation fails in pytests'''
    main_args = [x for x in list(args) if (x != 'sim' and '--seed' not in x)]
    return eda.main('sim', '--seed=1', *main_args)

def eda_elab_wrap(*args):
    '''Calls eda.main'''
    main_args = [x for x in list(args) if (x != 'elab' and '--seed' not in x)]
    return eda.main('elab', *main_args)

def assert_sim_log_passes(filepath:str, want_str='TEST PASS', err_strs=['Error', 'ERROR', 'TEST FAIL']) -> None:
    test_passed = False
    test_failed = False

    assert os.path.exists(filepath), f'{filepath=} does not exist'
    if not want_str:
        # we don't have a want_str, so looks like it passes no matter what
        test_passed = True
    with open(filepath) as f:
        for line in f.readlines():
            if want_str and want_str in line:
                test_passed = True
            if any([x in line for x in err_strs]):
                test_failed = True
    assert test_passed, f'{filepath=} did not have {want_str=}'
    assert not test_failed, f'{file_path} has one of {err_strs=}'

def assert_gen_deps_yml_good(filepath:str, want_target:str='') -> dict:
    '''Generated DEPS files should be coming from --export style args,

    so we also confirm they pass the deps_schema.FILE_SIMPLIFIED'''
    assert os.path.exists(filepath), f'{filepath=} does not exist'
    data = util.yaml_safe_load(filepath)
    assert len(data.keys()) > 0
    if want_target:
        assert want_target, f'{want_target=} not in {filepath=} {data=}'
        assert 'deps' in data[want_target], f' key "deps" is not in {want_target=} in {data=}'
    assert deps_schema.check_files(filepath, schema_obj=deps_schema.FILE_SIMPLIFIED)
    return data


def assert_export_json_good(filepath:str) -> dict:
    import json
    assert os.path.exists(filepath), f'{filepath=} does not exist'
    with open(filepath) as f:
        data = json.load(f)
    assert 'name' in data
    assert 'eda' in data
    assert any([x in data for x in ['files', 'tb']])
    return data


def assert_export_jsonl_good(filepath:str, jsonl:bool=True) -> list:
    import json
    assert os.path.exists(filepath), f'{filepath=} does not exist'
    ret = list()
    with open(filepath) as f:
        if jsonl:
            for line in f.readlines():
                line = line.strip()
                data = json.loads(line)
                assert 'name' in data
                assert 'eda' in data
                assert any([x in data for x in ['files', 'tb']])
                ret.append(data)
        else:
            data = json.load(f)
            assert 'tests' in data
            assert type(data['tests']) is list
            for entry in data['tests']:
                assert 'name' in entry
                assert 'eda' in entry
                assert any([x in entry for x in ['files', 'tb']])
                ret.append(entry)


    return ret


class Helpers:
    '''We do so much with logging in this file, might as well make it reusable'''
    DEFAULT_DIR = ''
    DEFAULT_LOG = 'eda.log'
    def chdir(self):
        chdir_remove_work_dir('', self.DEFAULT_DIR)

    def log_it(self, command_str:str, logfile=None, use_eda_wrap=True):
        '''
        rc = self.log_it('sim foo', logfile='yes.log')
        assert rc == 0
        '''
        if logfile is None:
            logfile = self.DEFAULT_LOG
        from contextlib import redirect_stdout, redirect_stderr
        with open(logfile, 'w') as f:
            with redirect_stdout(f):
                with redirect_stderr(f):
                    if use_eda_wrap:
                        rc = eda_wrap(*(command_str.split()))
                    else:
                        rc = eda.main(*(command_str.split()))
        return rc

    def is_in_log(self, *want_str, logfile=None):
        if logfile is None:
            logfile = self.DEFAULT_LOG
        want_str = ' '.join(list(want_str))
        with open(logfile) as f:
            for line in f.readlines():
                if want_str in line:
                    return True
        return False

    def get_log_lines_with(self, *want_str, logfile=None):
        if logfile is None:
            logfile = self.DEFAULT_LOG
        ret_list = []
        want_str = ' '.join(list(want_str))
        with open(logfile) as f:
            for line in f.readlines():
                if want_str in line:
                    ret_list.append(line)
        return ret_list

    def get_log_words_with(self, *want_str, logfile=None):
        if logfile is None:
            logfile = self.DEFAULT_LOG
        ret_list = []
        want_str = ' '.join(list(want_str))
        with open(logfile) as f:
            for line in f.readlines():
                if want_str in line:
                    for word in line.split():
                        if want_str in word:
                            ret_list.append(word)
        return ret_list
