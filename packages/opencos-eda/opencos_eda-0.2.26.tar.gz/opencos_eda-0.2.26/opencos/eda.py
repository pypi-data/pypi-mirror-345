#!/usr/bin/env python3

# SPDX-License-Identifier: MPL-2.0

import time
import subprocess
import os
import sys
import shutil
import re
import queue
import threading
import signal
import yaml
import argparse
import glob
import shlex
import copy

import opencos
from opencos import seed, deps_helpers, util, files
from opencos import eda_config
from opencos.deps_helpers import get_deps_markup_file, deps_markup_safe_load

# Globals

debug_respawn = False
util.progname = "EDA"

bash_exec = shutil.which('bash')

class Tool:
    error = util.error # use that module's method
    _TOOL = '' # this is the only place a class._TOOL should be set to non-empty str
    _URL = None
    _EXE = None

    def __init__(self, config: dict = {}):
        # Because Command child classes (CommandSimVerilator, for example), will
        # inherit both Command and Tool classes, we'd like them to reference
        # a Command object's self.args instead of the class Tool.args. Safely create it
        # if it doesn't exist:
        self._VERSION = None
        if getattr(self, 'args', None) is None:
            self.args = dict()
            self.args_help = dict()
        self.args.update({
            'tool':   self._TOOL, # Set for all derived classes.
            'xilinx': False,
        })
        self.args_help.update({
            'tool': 'Tool to use for this command, such as: verilator',
            'xilinx': 'Set to use XPMs, and other global Xilinx specific cells/libraries',
        })
        # update self._EXE if config says to:
        self.set_exe(config)
        self.get_versions()

    def set_exe(self, config: dict) -> None:
        if self._TOOL and self._TOOL in config.get('auto_tools_order', [{}])[0]:
            exe = config.get('auto_tools_order', [{}])[0][self._TOOL].get('exe', '')
            if exe and type(exe) is list:
                exe = exe[0] # pick first
            if exe and exe != self._EXE:
                util.info(f'Override for {self._TOOL} using exe {exe}')
                self._EXE = exe

    def get_full_tool_and_versions(self) -> str:
        '''Returns tool:version, such as: verilator:5.033'''
        if not self._VERSION:
            self.get_versions()
        return str(self._TOOL) + ':' + str(self._VERSION)

    def get_versions(self) -> str:
        '''Sets and returns self._VERSION'''
        return self._VERSION

    def set_tool_defines(self) -> None:
        pass


class Command:
    def __init__(self, config:dict, command_name:str):
        self.args = dict()
        self.args_help = dict()
        self.args.update({
            "keep" : False,
            "force" : False,
            "fake" : False,
            "stop-before-compile": False,   # Usually in the self.do_it() method, stop prior to compile/elaborate/simulate
            "stop-after-compile": False,
            "stop-after-elaborate": False,  # Set to True to only run compile + elaboration (aka compile + lint)
            "lint": False, # Same as stop-after-elaborate
            "eda-dir" : "eda.work", # all eda jobs go in here
            "job-name" : "", # this is used to create a certain dir under "eda_dir"
            "work-dir" : "", # this can be used to run the job in a certain dir, else it will be <eda-dir>/<job-name> else <eda-dir>/<target>_<command>
            "sub-work-dir" : "", # this can be used to name the dir built under <eda-dir>, which seems to be same function as job-name??
            "suffix" : "",
            "design" : "", # not sure how this relates to top
            'export':     False,
            'export-run': False,       # run from the exported location if possible, if not possible run the command in usual place.
            'export-json': False,      # generates an export.json suitable for a testrunner, if possible for self.command.
            'enable-tags': list(),
            'disable-tags': list(),
        })
        self.args_help.update({
            'stop-before-compile': 'stop this run before any compile (if possible for tool) and' \
            + ' save .sh scripts in eda-dir/',
            'eda-dir':     'relative directory where eda logs are saved',
            'export':      'export results for these targets in eda-dir',
            'export-run':  'export, and run, results for these targets in eda-dir',
            'export-json': 'export, and save a JSON file per target',
            'work-dir':    'Optional override for working directory, often defaults to ./eda.work/<top>.<command>',
            'enable-tags': 'DEPS markup tag names to be force enabled for this' \
            + ' command (mulitple appends to list).',
            'diable-tags': 'DEPS markup tag names to be disabled (even if they' \
            + ' match the criteria) for this command (mulitple appends to list).' \
            + ' --disable-tags has higher precedence than --enable-tags.'
        })
        self.modified_args = {}
        self.config = copy.deepcopy(config) # avoid external modifications.
        self.command_name = command_name
        self.target = ""
        self.status = 0

    def error(self, *args, **kwargs):
        '''Returns None, child classes can call self.error(..) instead of util.error, which updates their self.status.

        Please consider using Command.error(..) (or self.error(..)) in place of util.error so self.status is updated.
        '''
        self.status = util.error(*args, **kwargs)

    def status_any_error(self, report=True) -> bool:
        '''Used by derived classes process_tokens() to know an error was reached
        and to not perform the command. Necessary for pytests that use eda.main()'''
        if report and self.status > 0:
            util.error(f"command '{self.command_name}' has previous errors")
        return self.status > 0

    def which_tool(self, command:str):
        return which_tool(command, config=self.config)

    def create_work_dir(self):
        if (not os.path.exists(self.args['eda-dir'])): # use os.path.isfile / isdir also
            os.mkdir(self.args['eda-dir'])
        if self.args['design'] == "":
            if ('top' in self.args) and (self.args['top'] != ""):
                self.args['design'] = self.args['top']
            else:
                self.args['design'] = "design" # generic, i.e. to create work dir "design_upload"
        if self.target == "":
            self.target = self.args['design']
        if self.args['work-dir'] == '':
            if self.args['sub-work-dir'] == '':
                if self.args['job-name'] != '':
                    self.args['sub-work-dir'] = self.args['job-name']
                else:
                    self.args['sub-work-dir'] = f'{self.target}.{self.command_name}'
            self.args['work-dir'] = os.path.join(self.args['eda-dir'], self.args['sub-work-dir'])
        keep_file = os.path.join(self.args['work-dir'], "eda.keep")
        if (os.path.exists(self.args['work-dir'])):
            if os.path.exists(keep_file) and not self.args['force']:
                self.error(f"Cannot remove old work dir due to '{keep_file}'")
            util.info(f"Removing previous '{self.args['work-dir']}'")
            shutil.rmtree(self.args['work-dir'])
        os.mkdir(self.args['work-dir'])
        if (self.args['keep']):
            open(keep_file, 'w').close()
        util.info(f'Creating work-dir: {self.args["work-dir"]=}')
        return self.args['work-dir']

    def exec(self, work_dir, command_list, background=False, stop_on_error=True,
             quiet=False, tee_fpath=None, shell=False):
        if not quiet:
            util.info(f"exec: {' '.join(command_list)} (in {work_dir}, {tee_fpath=})")
        original_cwd = util.getcwd()
        os.chdir(work_dir)

        stdout, stderr, return_code = util.subprocess_run_background(
            work_dir=None, # we've already called os.chdir(work_dir).
            command_list=command_list,
            background=background,
            fake=self.args.get('fake', False),
            tee_fpath=tee_fpath,
            shell=shell
        )

        os.chdir(original_cwd)
        if return_code:
            self.status += return_code
            if stop_on_error: self.error(f"exec: returned with error (return code: {return_code})")
            else            : util.debug(f"exec: returned with error (return code: {return_code})")
        else:
            util.debug(f"exec: returned without error (return code: {return_code})")
        return stderr, stdout, return_code

    def set_arg(self, key, value):

        # Do some minimal type handling, preserving the type(self.args[key])

        if type(self.args[key]) is dict:
            # if dict, update
            self.args[key].update(value)

        elif type(self.args[key]) is list:
            # if list, append (no duplicates)
            if type(value) is list:
                for x in value:
                    if x not in self.args[key]:
                        self.args[key].append(x)
            elif value not in self.args[key]:
                self.args[key].append(value)

        elif type(self.args[key]) is bool:
            # if bool, then attempt to convert string or int
            if type(value) in [bool, int]:
                self.args[key] = bool(value)
            elif type(value) is str:
                if value.lower() in ['false', '0']:
                    self.args[key] = False
                else:
                    self.args[key] = True
            else:
                raise Exception(f'set_arg({key=}, {value=}) bool, {type(self.args[key])=} {type(value)=}')

        elif type(self.args[key]) is int:
            # if int, attempt to convert string or bool
            if type(value) in [bool, int, str]:
                self.args[key] = int(value)
            else:
                raise Exception(f'set_arg({key=}, {value=}) int, {type(self.args[key])=} {type(value)=}')


        else:
            # else overwrite it as-is.
            self.args[key] = value

        self.modified_args[key] = True
        util.debug(f'Set arg["{key}"]="{self.args[key]}"')


    def get_argparser(self) -> argparse.ArgumentParser:
        ''' Returns an argparse.ArgumentParser() based on self.args (dict)'''

        # Preference is --args-with-dashes, which then become parsed.args_with_dashes, b/c
        # parsed.args-with-dashes is not legal python. Some of self.args.keys() still have - or _, so
        # this will handle both.
        # Also, preference is for self.args.keys(), to be str with - dashes
        parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        bool_action_kwargs = util.get_argparse_bool_action_kwargs()
        for key,value in self.args.items():
            if '_' in key and '-' in key:
                assert False, f'{self.args=} has {key=} with both _ and -, which is not allowed'
            if '_' in key:
                util.warning(f'{key=} has _ chars, prefer -')

            keys = [key] # make a list
            if '_' in key:
                keys.append(key.replace('_', '-')) # switch to POSIX dashes for argparse
            elif '-' in key:
                keys.append(key.replace('-', '_')) # also support --some_arg_with_underscores

            arguments = list() # list supplied to parser.add_argument(..) so one liner supports both.
            for this_key in keys:
                arguments.append(f'--{this_key}')

            if self.args_help.get(key, ''):
                help_kwargs = {'help': self.args_help[key] + f' (default={value})'}
            elif value is None:
                help_kwargs = {'help': f'default={value}'}
            else:
                help_kwargs = {'help': f'{type(value).__name__} default={value}'}


            # It's important to set the default=None on these, except for list types where default is list()
            # If the parsed Namespace has values set to None or [], we do not update. This means that as deps
            # are processed that have args set, they cannot override the top level args that were already set.
            # nor be overriden by defaults.
            if type(value) is bool:
                # For bool, support --key and --no-key with this action=argparse.BooleanOptionalAction.
                # Note, this means you cannot use --some-bool=True, or --some-bool=False, has to be --some-bool
                # or --no-some-bool.
                parser.add_argument(
                    *arguments, default=None, **bool_action_kwargs, **help_kwargs)
            elif type(value) is list:
                parser.add_argument(*arguments, default=list(), action='append', **help_kwargs)
            elif type(value) in [int, str]:
                parser.add_argument(*arguments, default=None, type=type(value), **help_kwargs)
            elif value is None:
                parser.add_argument(*arguments, default=None, **help_kwargs)
            else:
                assert False, f'{key=} {value=} how do we do argparse for this type of value?'

        return parser


    def run_argparser_on_list(self, tokens:list, apply_parsed_args:bool=True):
        ''' Creates an argparse.ArgumentParser() for all the keys in self.args, and attempts to parse
        from the provided list. Parsed args are applied to self.args.

        Returns a list of the unparsed, or remaining, args from the provided list.

        If apply_parsed_args=False, returns a dict of parsed args (not applied) and a list of unparsed args.
        '''

        if len(tokens) == 0:
            return list()
        parser = self.get_argparser()
        try:
            parsed, unparsed = parser.parse_known_args(tokens + [''])
            unparsed = list(filter(None, unparsed))
        except argparse.ArgumentError:
            self.error(f'problem attempting to parse_known_args for {tokens=}')

        parsed_as_dict = vars(parsed)

        args_to_be_applied = dict()

        for key,value in parsed_as_dict.items():
            # key should have _ instead of POSIX dashes, but we still support dashes like self.args['build-file'],
            # etc.
            if key not in self.args and '_' in key:
                # try with dashes instead of _
                key = key.replace('_', '-')
            assert key in self.args, f'{key=} not in {self.args=}'

            args_to_be_applied[key] = value

        if apply_parsed_args:
            self.apply_args_from_dict(args_to_be_applied)
            return unparsed
        else:
            return args_to_be_applied, unparsed


    def apply_args_from_dict(self, args_to_be_applied:dict) -> list:
        for key,value, in args_to_be_applied.items():

            if value is None:
                continue # don't update a self.args[key] to None
            if type(value) is list and len(value) == 0:
                continue # don't update a self.args[key] that's a list() to an empty list.
            if type(value) is not list and self.modified_args.get(key, None):
                # For list types, we append. For all others they overwrite, so if we've already
                # modified the arg once, do not modify it again. Such as, command line set an arg,
                # but then a target tried to set it again; or a target set it, and then a dependent
                # target tried to set it again.
                util.warning(f"Command.run_argparser_on_list - skipping {key=} {value=}",
                             f" b/c arg is already modified (cur value=",
                             f"{self.args.get(key, None)})")
                continue
            if self.args[key] != value:
                util.debug(f"Command.run_argparser_on_list - setting set_arg b/c",
                           f" argparse -- {key=} {value=}")
                self.set_arg(key, value) # Note this has special handling for lists already.
                self.modified_args[key] = True


    def process_tokens(self, tokens, process_all=True):
        '''Command.process_tokens(..) for all named self.args.keys() returns the
        unparsed tokens list

        Derived classes do not need to return a list of unparsed args, nor
        return self.status
        '''

        unparsed = self.run_argparser_on_list(tokens)
        if process_all and len(unparsed) > 0:
            self.error(f"Didn't understand argument: '{unparsed=}' in",
                       f" {self.command_name=} context")

        return unparsed

    def set_tool_config_from_config(self):
        util.warning(f'{self.__class__.__name__} - set_tool_config_from_config not',
                     ' implemented for this command')
        # Not raising an exception, let CommandSim override, warn if others try this.
        # TODO(drew): implement for CommandSynth.
        pass

    def update_tool_config(self):
        # Not raising an exception, let CommandSim override
        pass

    def write_eda_config_and_args(self):
        if not self.args.get('work-dir', None):
            util.warning(f'Ouput work-dir not set, saving ouput eda_config to {os.getcwd()}')
        util.write_eda_config_and_args(dirpath=self.args.get('work-dir', os.getcwd()),
                                       command_obj_ref=self)

    def is_export_enabled(self) -> bool:
        # check if any self.args['export'] is set in any way (but not set to False
        # or empty list)
        return any([arg.startswith('export') and v for arg,v in self.args.items()])

    def run(self):
        self.do_it()

    def do_it(self):
        self.write_eda_config_and_args()
        self.error(f"No tool bound to command '{self.command_name}', you",
                   " probably need to setup tool, or use '--tool <name>'")

    def help(self, tokens: list = []):
        '''Since we don't quite follow standard argparger help()/usage(), we'll format our own

        if self.args_help has additional help information.
        '''

        # Indent long lines (>100) to indent=56 (this is where we leave off w/ {vstr:12} below.
        def indent_me(text:str):
            return util.indent_wrap_long_text(text, width=100, indent=56)

        util.info('Help:')
        # using bare 'print' here, since help was requested, avoids --color and --quiet
        print()
        print('Usage:')
        print(f'    eda [options] {self.command_name} [options] [files|targets, ...]')
        print()

        print_base_help()
        lines = []
        if self.command_name:
            lines.append(f"Generic help for command='{self.command_name}' (using '{self.__class__.__name__}')")
        else:
            lines.append(f"Generic help (from class Command):")

        # Attempt to run argparser on args, but don't error if it fails.
        unparsed = list()
        if tokens:
            try:
                unparsed = self.run_argparser_on_list(tokens=tokens)
            except:
                pass

        for k in sorted(self.args.keys()):
            v = self.args[k]
            vstr = str(v)
            khelp = self.args_help.get(k, '')
            if khelp:
                khelp = f'  - {khelp}'
            if type(v) == bool :
                lines.append(indent_me(f"  --{k:20} : boolean    : {vstr:12}{khelp}"))
            elif type(v) == int:
                lines.append(indent_me(f"  --{k:20} : integer    : {vstr:12}{khelp}"))
            elif type(v) == list:
                lines.append(indent_me(f"  --{k:20} : list       : {vstr:12}{khelp}"))
            elif type(v) == str:
                vstr = "'" + v + "'"
                lines.append(indent_me(f"  --{k:20} : string     : {vstr:12}{khelp}"))
            else:
                lines.append(indent_me(f"  --{k:20} : <unknown>  : {vstr:12}{khelp}"))
        lines.append('')
        for line in lines:
            print(line)

        if unparsed:
            print(f'Unparsed args: {unparsed}')


class CommandDesign(Command):

    # Used by for DEPS work_dir_add_srcs@ commands, by class methods:
    #   update_file_lists_for_work_dir(..), and resolve_target(..)
    _work_dir_add_srcs_path_string = '@EDA-WORK_DIR@'

    # Optionally error in self.process_tokens, derived classes can override.
    error_on_no_files_or_targets = False
    error_on_missing_top = False

    def __init__(self, config:dict, command_name:str):
        Command.__init__(self, config=config, command_name=command_name)
        self.args.update({
            'seed': seed.get_seed(style="urandom"),
            'top': '',
            'all-sv': False,
            'unprocessed-plusargs': list(),
        })
        self.args_help.update({
            'seed':   'design seed, default is 31-bit non-zero urandom',
            'top':    'TOP level verilog/SV module or VHDL entity for this target',
            'all-sv': 'Maintain .sv and .v in single file list. (if False: .sv flist separate from .v flist)',
            'unprocessed-plusargs': 'Args that began with +, but were not +define+ or +incdir+, +<name>, ' \
            + ' or +<name>=<value>. These become tool dependent, for example "sim" commands will treat as sim-plusargs',
        })
        self
        self.defines = dict()
        self.incdirs = list()
        self.files = dict()
        self.files_v = list()
        self.files_sv = list()
        self.files_vhd = list()
        self.files_cpp = list()
        self.files_non_source = list()
        self.files_caller_info = dict()
        self.dep_shell_commands = list() # each list entry is a dict()
        self.dep_work_dir_add_srcs = set() # key: tuple (target_path, target_node, filename)
        self.oc_root = util.get_oc_root()
        for (d,v) in self.config.get('defines', dict()).items():
            self.defines[d] = v

        self.cached_deps = dict() # key = abspath of DEPS markup file, has sub-dicts for 'data' and 'line_numbers'.
        self.targets_dict = dict() # key = targets that we've already processed in DEPS files

    def run_dep_commands(self):
        # Run any shell@ commands from DEPS files
        self.run_dep_shell_commands()
        # Update any work_dir_add_srcs@ in our self.files, self.files_v, etc, b/c
        # self.args['work-dir'] now exists.
        self.update_file_lists_for_work_dir()
        # Link any non-sources to our work-dir:
        self.update_non_source_files_in_work_dir()

    def run_dep_shell_commands(self):
        # Runs from self.args['work-dir']
        all_cmds_lists = list()

        log_fnames_count = dict() # count per target_node.

        for iter, d in enumerate(self.dep_shell_commands):
            clist = util.ShellCommandList(d['exec_list'])
            log = clist.tee_fpath
            target_node = d["target_node"]
            if clist.tee_fpath is None:
                lognum = log_fnames_count.get(target_node, 0)
                log = f'{target_node}__shell_{lognum}.log' # auto log every shell command.
                clist.tee_fpath = log
                # In case some single target has N shell commands, give them unique log names.
                log_fnames_count.update({target_node: lognum + 1})
            all_cmds_lists += [
                [], # blank line
                # comment, where it came from, log to {node}__shell_{lognum}.log (or tee name from DEPS.yml)
                [f'# command {iter}: target: {d["target_path"]} : {target_node} --> {log}'],
                # actual command (list or util.ShellCommandList)
                clist,
            ]
            d['exec_list'] = clist # update to tee_fpath is set.

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='pre_compile_dep_shell_commands.sh',
                                      command_lists=all_cmds_lists)

        for iter,d in enumerate(self.dep_shell_commands):
            util.info(f'run_dep_shell_commands {iter=}: {d=}')
            clist = util.ShellCommandList(d['exec_list'])
            # NOTE(drew): shell=True subprocess call, can disable with self.config
            self.exec(self.args['work-dir'], clist, tee_fpath=clist.tee_fpath,
                      shell=self.config.get('deps_subprocess_shell', False))

    def update_file_lists_for_work_dir(self):
        if len(self.dep_work_dir_add_srcs) == 0:
            return

        # If we encounter any @EDA-WORK_DIR@some_file.v in self.files, self.files_v, etc, then replace it with:
        # self.args['work-dir'] / some_file.v:
        _work_dir_add_srcs_path_string_len = len(self._work_dir_add_srcs_path_string)
        work_dir_abspath = os.path.abspath(self.args['work-dir'])
        for key in list(self.files.keys()): # list so it's not an iterator, we're updating self.files.
            if type(key) is str and key.startswith(self._work_dir_add_srcs_path_string):
                new_key = os.path.join(work_dir_abspath, key[_work_dir_add_srcs_path_string_len :])
                self.files.pop(key)
                self.files[new_key] = True

        my_file_lists_list = [self.files_v, self.files_sv, self.files_vhd, self.files_cpp]
        for my_file_list in my_file_lists_list:
            for iter,value in enumerate(my_file_list):
                if value and type(value) is str and value.startswith(self._work_dir_add_srcs_path_string):
                    new_value = os.path.join(work_dir_abspath, value[_work_dir_add_srcs_path_string_len :])
                    my_file_list[iter] = new_value
                    util.debug(f"file lists: replaced {value} with {new_value}")

    def update_non_source_files_in_work_dir(self):
        for fname in self.files_non_source:
            _, leaf_fname = os.path.split(fname)
            destfile = os.path.join(self.args['work-dir'], leaf_fname)
            relfname = os.path.relpath(fname)
            caller_info = self.files_caller_info[fname]
            if not os.path.exists(fname):
                util.info(f'{fname=} {self.files_caller_info=}')
                self.error(f'Non-source file (reqs?) {relfname=} does not exist from {caller_info}')
            elif not os.path.exists(destfile):
                util.debug(f'updating non-source file to work-dir: Linked {fname=} to {destfile=}, from {caller_info}')
                os.symlink(src=fname, dst=destfile)

    def get_top_name(self, name):
        return os.path.splitext(os.path.basename(name))[0]

    def process_plusarg(self, plusarg:str, pwd=os.getcwd()):
        '''Retuns str, parses a +define+, +incdir+, or +key=value str and adds to self.defines, self.incdirs,

        or adds to self.args['unprocessed-plusargs'] (list) (and retuns value added to unprocessed-plusargs). '''
        # Since this may be coming from a raw CLI/bash argparser, we may have
        # args that come from shlex.quote(token), such as:
        #   token = '\'+define+OC_ROOT="/foo/bar/opencos"\''
        # So we strip all outer ' or " on the plusarg:
        plusarg = util.strip_outer_quotes(plusarg)
        if pwd is None:
            pwd = ''

        if plusarg.startswith('+define+'):
            plusarg = plusarg.lstrip('+define+')
            m = re.match(r'^(\w+)$', plusarg)
            if m:
                k = m.group(1)
                self.defines[k] = None
                util.debug(f"Defined {k}")
                return None
            m = re.match(r'^(\w+)\=(\S+)$', plusarg)
            if not m: m = re.match(r'^(\w+)\=(\"[^\"]*\")$', plusarg)
            if m:
                k = m.group(1)
                v = m.group(2)
                if v and type(v) is str:
                    if v.startswith('%PWD%/'):
                        v = v.replace('%PWD%', os.path.abspath(pwd))
                    if v.startswith('%SEED%'):
                        v = v.replace('%SEED%', str(self.args.get('seed', 1)))
                self.defines[k] = v
                util.debug(f"Defined {k}={v}")
                return None
            self.error(f"Didn't understand +define+: '{plusarg}'")
            return None

        if plusarg.startswith('+incdir+'):
            plusarg = plusarg.lstrip('+incdir+')
            m = re.match(r'^(\S+)$', plusarg)
            if m:
                incdir = m.group(1)
                if incdir not in self.incdirs:
                    self.incdirs.append(os.path.abspath(incdir))
                    util.debug(f"Added include dir '{os.path.abspath(incdir)}'")
                return None
            self.error(f"Didn't understand +incdir+: '{plusarg}'")
            return None

        # remaining plusargs as stored in self.args['unprocessed-plusargs'] (list)
        if plusarg.startswith('+'):
            if not self.config.get('bare_plusarg_supported', False):
                self.error(f"bare plusarg(s) are not supported: {plusarg}'")
                return None
            elif plusarg not in self.args['unprocessed-plusargs']:
                self.args['unprocessed-plusargs'].append(plusarg)
                # For anything added to unprocessed-plusarg, we have to return it, to let
                # derived classes have the option to handle it
                return plusarg
        else:
            self.error(f"Didn't understand +plusarg: '{plusarg}'")
        return None


    def append_shell_commands(self, cmds : list):
        # Each entry in cmds (list) should be a dict with keys ['target_node', 'target_path', 'exec_list']
        for entry in cmds:
            if entry is None or type(entry) is not dict:
                continue
            if entry in self.dep_shell_commands:
                # we've already run this exact command (target node, target path, exec list), don't run it
                # again
                continue

            assert 'exec_list' in entry, f'{entry=}'
            util.debug(f'adding - dep_shell_command: {entry=}')
            self.dep_shell_commands.append(entry)

    def append_work_dir_add_srcs(self, add_srcs: list, caller_info: str):
        # Each entry in add_srcs (list) should be a dict with keys ['target_node', 'target_path', 'file_list']
        for entry in add_srcs:
            if entry is None or type(entry) is not dict:
                continue

            work_dir_files = entry['file_list']
            for filename in work_dir_files:
                # Unfortunately, self.args['work-dir'] doesn't exist yet and hasn't been set, so we'll add these
                # files as '@EDA-WORK_DIR@' + filename, and have to replace the EDA-WORK_DIR@ string later in our flow.
                filename_use = self._work_dir_add_srcs_path_string + filename
                dep_key_tuple = (
                    entry['target_path'],
                    entry['target_node'],
                    filename_use
                )
                if filename_use not in self.files:
                    util.debug(f'work_dir_add_srcs@ {dep_key_tuple=} added file {filename_use=}')
                    self.add_file(filename=filename_use, use_abspath=False, caller_info=caller_info)
                    # avoid duplicate calls, and keep a paper trail of which DEPS added
                    # files from the self.args['work-dir'] using this method.
                    self.dep_work_dir_add_srcs.add(dep_key_tuple) # add to set()
                elif dep_key_tuple not in self.dep_work_dir_add_srcs:
                    # we've already added the file so this dep was skipped for this one file.
                    util.warning(f'work_dir_add_srcs@ {dep_key_tuple=} but {filename_use=}' \
                                 + 'is already in self.files (duplicate dependency on generated file?)')


    def resolve_target(self, target, no_recursion=False, caller_info=''):
        util.debug("Entered resolve_target(%s)" % (target))
        # self.target is a name we grab for the job (i.e. for naming work dir etc).  we don't want the path prefix.
        # TODO: too messy -- there's also a self.target, args['job-name'], args['work-dir'], args['design'], args['top'], args['sub-work-dir'] ...
        self.target = target
        m = re.match(r'.*\/([\w\-]+)$', self.target)
        if m: self.target = m.group(1)


        if target in self.targets_dict:
            # If we're encountered this target before, stop. We're not traversing again.
            return True

        self.targets_dict[target] = None
        file_exists, fpath, forced_extension = files.get_source_file(target)
        if file_exists:
            # If the target is a file (we're at the root here processing CLI arg tokens)
            # and that file exists and has an extension, then there's no reason to go looking
            # in DEPS files, add the file and return True.
            file_base, file_ext = os.path.splitext(fpath)
            if forced_extension or file_ext:
                self.add_file(fpath, caller_info=caller_info,
                              forced_extension=forced_extension)
                return True

        return self.resolve_target_core(target, no_recursion, caller_info)

    def resolve_target_core(self, target, no_recursion, caller_info=''):
        util.debug("Entered resolve_target_core(%s)" % (target))
        found_target = False
        util.debug("Starting to resolve target '%s'" % (target))
        target_path, target_node = os.path.split(target)

        deps = None
        data = None
        found_deps_file = False

        if self.config['deps_markup_supported']:
            deps = deps_helpers.DepsFile(
                command_design_ref=self, target_path=target_path, cache=self.cached_deps
            )
            deps_file = deps.deps_file
            data = deps.data
            data_only_lines = deps.line_numbers

        # Continue if we have data, otherwise look for files other than DEPS.<yml|yaml>
        if data is not None:
            found_deps_file = True
            found_target = deps.lookup(target_node=target_node, caller_info=caller_info)

        if found_deps_file and found_target:

            entry = deps.get_entry(target_node=target_node)

            # For convenience, use an external class for this DEPS.yml table/dict
            # This could be re-used for any markup DEPS.json, DEPS.toml, DEPS.py, etc.
            deps_processor = deps_helpers.DepsProcessor(
                command_design_ref = self,
                deps_entry = entry,
                target = target,
                target_path = target_path,
                target_node = target_node,
                deps_file = deps_file,
                # Update the caller_info for this DEPS.yml file's target_node, b/c we're now
                # examining this entry (target) in this deps_file.
                caller_info = deps.gen_caller_info(target_node)
            )

            # Process the target, and get new (unprocessed) deps entries list.
            # This updates self (for defines, incdirs, top, args, etc)
            # This will skip remaining deps in self.targets_dict
            deps_targets_to_resolve = deps_processor.process_deps_entry()
            util.debug(f'   ... for {target_node=} {deps_file=}, {deps_targets_to_resolve=}')

            # Recurse on the returned deps (ordered list), if they haven't already been traversed.
            for x in deps_targets_to_resolve:
                caller_info = deps.gen_caller_info(target_node)
                if x and type(x) is tuple:
                    # if deps_processor.process_deps_entry() gave us a tuple, it's an
                    # unprocessed 'command' that we kept in order until now. Append it.
                    assert len(x) == 2, f'command tuple {x=} must be len 2, {target_node=} {deps_file=}'
                    shell_commands_list, work_dir_add_srcs_list = x
                    self.append_shell_commands( cmds=shell_commands_list )
                    self.append_work_dir_add_srcs( add_srcs=work_dir_add_srcs_list,
                                                   caller_info=caller_info )

                elif x and x not in self.targets_dict:
                    self.targets_dict[x] = None # add it before processing.
                    file_exists, fpath, forced_extension = files.get_source_file(x)
                    if file_exists:
                        self.add_file(filename=fpath, caller_info=caller_info,
                                      forced_extension=forced_extension)
                    else:
                        util.debug(f'   ... Calling resolve_target_core({x=})')
                        found_target |= self.resolve_target_core( x, no_recursion, caller_info=caller_info)


        # Done with DEPS.yml if it existed.

        if not found_target:
            util.debug("Haven't been able to resolve %s via DEPS" % (target))
            known_file_extensions_for_source = []
            for x in ['verilog', 'systemverilog', 'vhdl', 'cpp']:
                known_file_extensions_for_source += self.config.get('file_extensions', {}).get(x, [])
            for e in known_file_extensions_for_source:
                try_file = target + e
                util.debug("Looking for %s" % (try_file))
                if os.path.exists(try_file):
                    self.add_file(try_file, caller_info=str('n/a::' + target + '::n/a'))
                    found_target = True
                    break # move on to the next target
            if not found_target: # if STILL not found_this_target...
                self.error("Unable to resolve target '%s'" % (target))

        # if we've found any target since being called, it means we found the one we were called for
        return found_target

    def add_file(self, filename, use_abspath=True, add_to_non_sources=False,
                 caller_info:str='', forced_extension:str=''):
        file_base, file_ext = os.path.splitext(filename)
        if use_abspath:
            file_abspath = os.path.abspath(filename)
        else:
            file_abspath = filename


        if file_abspath in self.files:
            util.debug("Not adding file %s, already have it" % (file_abspath))
            return

        known_file_ext_dict = self.config.get('file_extensions', {})
        v_file_ext_list = known_file_ext_dict.get('verilog', [])
        sv_file_ext_list = known_file_ext_dict.get('systemverilog', [])
        vhdl_file_ext_list = known_file_ext_dict.get('vhdl', [])
        cpp_file_ext_list = known_file_ext_dict.get('cpp', [])

        if forced_extension:
            # If forced_extension='systemverilog', then use the first known extension for
            # it ('.sv', from eda_config_defaults.yml), which will pick it up in the if-elif
            # below.
            file_ext = known_file_ext_dict.get(forced_extension, [''])[0]
            util.debug(f"{forced_extension=} for {filename=} as type '{file_ext}'")

        if add_to_non_sources:
            self.files_non_source.append(file_abspath)
            util.debug("Added non-source file file %s as %s" % (filename, file_abspath))
        elif file_ext in v_file_ext_list and not self.args['all-sv']:
            self.files_v.append(file_abspath)
            util.debug("Added Verilog file %s as %s" % (filename, file_abspath))
        elif file_ext in sv_file_ext_list or ((file_ext in v_file_ext_list) and self.args['all-sv']):
            self.files_sv.append(file_abspath)
            util.debug("Added SystemVerilog file %s as %s" % (filename, file_abspath))
        elif file_ext in vhdl_file_ext_list:
            self.files_vhd.append(file_abspath)
            util.debug("Added VHDL file %s as %s" % (filename, file_abspath))
        elif file_ext in cpp_file_ext_list:
            self.files_cpp.append(file_abspath)
            util.debug("Added C++ file %s as %s" % (filename, file_abspath))
        else:
            # unknown file extension. In these cases we link the file to the working directory
            # so it is available (for example, a .mem file that is expected to exist with relative path)
            self.files_non_source.append(file_abspath)
            util.debug("Added non-source file %s as %s" % (filename, file_abspath))

        self.files[file_abspath] = True
        self.files_caller_info[file_abspath] = caller_info
        return file_abspath

    def process_tokens(self, tokens, process_all=True, pwd=None):
        util.debug(f'CommandDesign - process_tokens start - {tokens=}')

        # see if it's a flag/option like --debug, --seed <n>, etc
        # This returns all unparsed args, and doesn't error out due to process_all=False
        orig_tokens = tokens.copy()
        unparsed = Command.process_tokens(self, tokens, process_all=False)
        util.debug(f'CommandDesign - after Command.process_tokens(..) {unparsed=}')

        # deal with +define+ or +incdir+, consume it and remove from unparsed
        # walk the list, remove all items after we're done.
        remove_list = list()
        for token in unparsed:
            # Since this is a raw argparser, we may have args that come from shlex.quote(token), such as:
            # token = '\'+define+OC_ROOT="/foo/bar/opencos"\''
            # So we have to check for strings that have been escaped for shell with extra single quotes.
            m = re.match(r"^\'?\+\w+", token)
            if m:
                # Copy and strip all outer ' or " on the plusarg:
                plusarg = util.strip_outer_quotes(token)
                self.process_plusarg(plusarg, pwd=pwd)
                remove_list.append(token)
        for x in remove_list:
            unparsed.remove(x)

        if len(unparsed) == 0 and self.error_on_no_files_or_targets:
            # derived classes can set error_on_no_files_or_targets=True
            # For example: CommandSim will error (requires files/targets),
            # CommandWaves does not (files/targets not required)
            # A nice-to-have: if someone ran: eda sim; without a file/target,
            # check the DEPS markup file for a single target, and if so run it
            # on the one and only target.
            if self.config['deps_markup_supported']:
                deps = deps_helpers.DepsFile(
                    command_design_ref=self, target_path=os.getcwd(), cache=self.cached_deps
                )
                if deps.deps_file and deps.data:
                    all_targets = deps_helpers.deps_data_get_all_targets(deps.data)
                    if len(all_targets) == 1:
                        target = all_targets[0]
                        unparsed.append(target)
                        util.info(f"For command '{self.command_name}' no files or targets were",
                                  f"presented at the command line, so using '{target}' from",
                                  f"{deps.deps_file}")
            if len(unparsed) == 0:
                # If unparsed is still empty, then error.
                self.error(f"For command '{self.command_name}' no files or targets were",
                           f"presented at the command line: {orig_tokens}")


        # by this point hopefully this is a target ... is it a simple filename?
        remove_list = list()
        last_potential_top = None # used for 'top' if top not specified.
        last_potential_top_path = None
        last_potential_top_isfile = False
        caller_info = ''
        for token in unparsed:
            file_exists, fpath, forced_extension = files.get_source_file(token)
            if file_exists:
                file_abspath = os.path.abspath(fpath)
                file_base, file_ext = os.path.splitext(file_abspath)
                if not forced_extension and not file_ext:
                    # This probably isn't a file we want to use
                    util.warning(f'looking for deps {token=}, found {file_abspath=}' \
                                 + ' but has no file extension, we will not add this file')
                    # do not consume it, it's probably a named target in DEPS.yml
                else:
                    self.add_file(filename=fpath, caller_info=caller_info,
                                  forced_extension=forced_extension)

                    known_file_ext_dict = self.config.get('file_extensions', {})
                    if forced_extension:
                        # If forced_extension='systemverilog', then use the first known extension for
                        # it ('.sv', from eda_config_defaults.yml):
                        file_ext = known_file_ext_dict.get(forced_extension, [''])[0]

                    if not self.args['top'] and \
                       file_ext and \
                       file_ext in known_file_ext_dict.get('inferred_top', []):
                        # if we haven't yet been given a top, or inferred one, we take the last one we get
                        # from a raw list of RTL file names (from args or command line tokens)
                        last_potential_top_path = file_abspath
                        last_potential_top = self.get_top_name(file_abspath)
                        last_potential_top_isfile = True

                    remove_list.append(token)
                    continue # done with token, consume it, we added the file.

            # we appear to be dealing with a target name which needs to be resolved (usually recursively)
            if token.startswith(os.sep):
                target_name = token # if it's absolute path, don't prepend anything
            else:
                target_name = os.path.join(".", token) # prepend ./so that we always have a <path>/<file>

            util.debug(f'Calling self.resolve_target on {target_name=}')
            if self.resolve_target(target_name, caller_info=caller_info):
                if self.args['top'] == '':
                    # if we haven't yet been given a top, or inferred one, we take the last named target
                    # from args or command line tokens
                    # from a target name
                    last_potential_top = self.get_top_name(target_name)
                    last_potential_top_path = target_name
                    last_potential_top_isfile = False

                remove_list.append(token)
                continue # done with token

        for x in remove_list:
            unparsed.remove(x)

        # we were unable to figure out what this command line token is for...
        if process_all and len(unparsed) > 0:
            self.error(f"Didn't understand command remaining tokens {unparsed=} in CommandDesign")

        # handle a missing self.args['top'] with last filepath.
        if self.args.get('top', '') == '' and last_potential_top is not None:
            self.args['top'] = last_potential_top
            self.args['top-path'] = last_potential_top_path
            util.info(f"Inferred --top {self.args['top']} {self.args['top-path']}")
            if last_potential_top_isfile:
                # top wasn't set, we're using the final command-line 'arg' filename (not from DEPS.yml)
                # need to override self.target if that was set. Otherwise it won't save to the correct
                # work-dir:
                self.target = last_potential_top
        if self.error_on_missing_top and not self.args.get('top', ''):
            self.error(f"Did not get a --top or DEPS top, required to run command",
                       f"'{self.command_name}' for tool={self.args.get('tool', None)}")


    def get_command_line_args(self, remove_args:list=[], remove_args_startswith:list=[]) -> list:
        '''Returns a list of all the args if you wanted to re-run this command
        (excludes eda, command, target).'''

        # This will not set bool's that are False, does not add --no-<somearg>
        # nor --<somearg>=False
        # This will not set str's that are empty.
        # this will not set ints that are 0
        ret = list()
        for k,v in self.args.items():

            # Some args cannot be extracted and work, so omit these:
            if k in ['top-path'] + remove_args:
                continue
            if any([k.startswith(x) for x in remove_args_startswith]):
                continue

            if type(v) is bool and v:
                ret.append(f'--{k}')
            elif type(v) is int and bool(v):
                ret.append(f'--{k}={v}')
            elif type(v) is str and v:
                ret.append(f'--{k}={v}')
            elif type(v) is list:
                for item in v:
                    if item or type(item) not in [bool, str]:
                        # don't print bool/str that are blank.
                        ret.append(f'--{k}={item}') # lists append

        return ret


class CommandExport(CommandDesign):

    error_on_no_files_or_targets = True
    error_on_missing_top = True

    def __init__(self, config:dict):
        CommandDesign.__init__(self, config=config, command_name="export")
        self.args.update({
            'output': "",

            # flatten mode is envisioned to remove all the dir hierarchy and write files into a single dir, good
            # for squeezing down into a simple extracted case (perhaps to create a bug report).  This is envisioned
            # as part of getting "eda" sims running through testrunner API.
            'flatten': False,
        })


    def process_tokens(self, tokens, process_all=True):
        self.defines['OC_EXPORT'] = None
        CommandDesign.process_tokens(self, tokens, process_all)
        if self.status_any_error():
            return
        if self.args['top']:
            # create our work dir, b/c top is set. We do this so any shell or peakrdl style
            # commands from DEPS can run in eda.work/{target}.export/
            # The final exported output (files and/or linked files) will be in
            # eda.export/{target}.export/
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()

    def do_it(self):
        from opencos import export_helper

        # decide output dir name
        if self.args['output'] == "":
            self.args['output'] = os.path.join('.', 'eda.export', self.args['top'] + '.export')
        out_dir = self.args['output']

        if not self.target:
            target = 'export'
        else:
            # Note this may not be the correct target for debug infomation,
            # for example if you passed several files as targets on the
            # command line, so we'll fall back to using self.target
            target = self.target

        export_obj = export_helper.ExportHelper( cmd_design_obj=self,
                                                 eda_command=self.command_name,
                                                 out_dir=out_dir,
                                                 target=target )

        self.write_eda_config_and_args()
        export_obj.run(check_if_overwrite=True)

    def set_tool_defines(self):
        pass

    # Methods that derived classes may override:
    def prepare_compile(self):
        self.set_tool_defines()

class CommandSim(CommandDesign):

    CHECK_REQUIRES = [Tool] # Used by check_command_handler_cls()
    error_on_no_files_or_targets = True
    error_on_missing_top = True

    def __init__(self, config:dict):
        CommandDesign.__init__(self, config=config, command_name="sim")
        self.args.update({
            "pre-sim-tcl": list(),
            'compile-args': list(),
            'elab-args': list(),
            'sim-args': list(),
            'sim-plusargs': list(), # lists are handled by 'set_arg(k,v)' so they append.
            'sim-library': list(),
            'coverage': False,
            'waves': False,
            'waves-start': 0,
            'pass-pattern': "",
            'optimize': False,
            'log-bad-strings': ['ERROR: ', 'FATAL: ', 'Error: ', 'Fatal: '],
            'log-must-strings': list(),
            # verilate-args: list of args you can only pass to Verilator, not used by other simulators, so
            # these can go in DEPS files for custom things like -CFLAGS -O0, etc.
            'verilate-args': list(),
        })
        self.args_help.update({
            'compile-args': 'args added to sim/elab "compile" step',
            'coverage': 'attempt to run coverage steps on the compile/elab/simulation',
            'elab-args':    'args added to sim/elab "elaboration" step, if required by tool',
            'log-bad-strings': 'strings that if present in the log will fail the simulation',
            'log-must-strings': 'strings that are required by the log to not-fail the simulation.' \
            + ' Some tools use these at only certain phases (compile/elab/sim).',
            'pass-pattern': 'Additional string required to pass a simulation, appends to log-must-strings',
            'sim-args':      'args added to final "simulation" step',
            'sim-plusargs':  '"simulation" step run-time args passed to tool, these can also be set using' \
            + ' --sim-plusargs=name[=value], or simply +name[=value]',
            'stop-before-compile': 'Create work-dir sh scripts for compile/elab/simulate, but do not run them.',
            'stop-after-compile': 'Create work-dir sh scripts, but only run the compile step.',
            'stop-after-elaborate': 'Create work-dir sh scripts, but run compile+elab, skip simulation step.',
            'top': 'Name of topmost Verilog/SystemVerilog module, or VHDL entity',
            'verilate-args': 'args added to "compile" step in Verilator simulation (for --tool=verilator)',
            'waves': 'Include waveforms, if possible for tool',
            'waves-start': 'Starting time of waveform capture, if possible for tool',
            'work-dir': 'Optional override for working directory, defaults to ./eda.work/<top>.sim',

        })


        self.args['verilate-args'] = list()

    def process_plusarg(self, plusarg: str, pwd: str = os.getcwd()):
        '''Override for CommandDesign.process_plusarg(..)'''
        maybe_plusarg = CommandDesign.process_plusarg(self, plusarg, pwd)
        # Support for self.args['unprocessed-plusargs'] --> self.args['sim-plusargs']:
        if maybe_plusarg and \
           maybe_plusarg in self.args['unprocessed-plusargs'] and \
           maybe_plusarg not in self.args['sim-plusargs']:
            self.args['sim-plusargs'].append(maybe_plusarg)
            self.args['unprocessed-plusargs'].remove(maybe_plusarg)
            util.debug(f'For parent "sim" command (CommandSim), moved plusarg: {maybe_plusarg}',
                       f'to sim-plusargs (from unprocessed-plusargs)')
        return None

    def process_tokens(self, tokens, process_all=True):
        self.defines['SIMULATION'] = None
        CommandDesign.process_tokens(self, tokens, process_all)

        if self.status_any_error():
            return

        # add defines for this job type
        if self.args['lint'] or self.args['stop-after-elaborate']:
            self.args['lint'] = True
            self.args['stop-after-elaborate'] = True
        if self.args['top']:
            # create our work dir
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()


    def set_tool_config_from_config(self):
        '''Sets self.tool_config (from original --config-yml=YAML|Default) and overrides
        self.defines, and self.args log-must-strings and log-bad-strings.'''
        tool = self.args.get('tool', '') # get from Command's self.args['tool']
        if tool:
            self.tool_config = self.config.get('tools', {}).get(tool, {})
            self.override_log_strings_from_tool_config()
            self.defines.update(self.tool_config.get('defines', {}))
            util.debug(f'set_tool_config_from_config: {tool=}')

    def update_tool_config(self):
        self.override_log_strings_from_tool_config()


    def override_log_strings_from_tool_config(self):
        if not getattr(self, 'tool_config', None):
            return
        # Collect (overwrite CommandSim) the bad and must strings, if present, from our config.tools.verilator:
        for tool_config_key in ['log-bad-strings', 'log-must-strings']:
            if len(self.tool_config.get(tool_config_key, [])) > 0:
                self.args[tool_config_key] = self.tool_config.get(tool_config_key, [])


    # Methods that derived classes may override:
    def run_commands_check_logs(self, commands, check_logs=True, log_filename=None,
                                bad_strings=[], must_strings=[],
                                use_bad_strings=True, use_must_strings=True):
        for obj in commands:

            assert isinstance(obj, list), \
                f'{self.target=} command {obj=} is not a list or util.ShellCommandList, not going to run it.'

            clist = list(obj).copy()
            tee_fpath = getattr(obj, 'tee_fpath', None)

            util.debug(f'run_commands_check_logs: {clist=}, {tee_fpath=}')

            log_fname = None
            if tee_fpath:
                log_fname = tee_fpath
            if log_filename:
                log_fname = log_filename

            self.exec(work_dir=self.args['work-dir'], command_list=clist, tee_fpath=tee_fpath)

            if check_logs and log_fname:
                self.check_logs_for_errors(
                    filename=log_fname, bad_strings=bad_strings, must_strings=must_strings,
                    use_bad_strings=use_bad_strings, use_must_strings=use_must_strings
                )

    def do_export(self):
        from opencos import export_helper

        out_dir = os.path.join(self.args['work-dir'], 'export')

        target = self.target
        if not target:
            target = 'test'

        export_obj = export_helper.ExportHelper( cmd_design_obj=self,
                                                 eda_command=self.command_name,
                                                 out_dir=out_dir,
                                                 # Note this may not be the correct target for debug infomation,
                                                 # so we'll only have the first one.
                                                 target=target )

        # Set things in the exported: DEPS.yml
        tool = self.args.get('tool', None)
        # Certain args are allow-listed here
        deps_file_args = list()
        for a in self.get_command_line_args():
            if any([a.startswith(x) for x in [
                    '--compile-args',
                    '--elab-args',
                    '--sim-',
                    '--coverage',
                    '--waves',
                    '--pass-pattern',
                    '--optimize',
                    '--stop-',
                    '--lint-',
                    '--verilate',
                    '--verilator']]):
                deps_file_args.append(a)

        export_obj.run(
            deps_file_args=deps_file_args,
            export_json_eda_config={
                'tool': tool,
            }
        )

        if self.args['export-run']:

            # remove the '--export' named args, we don't want those.
            args_no_export = self.get_command_line_args(remove_args_startswith=['export'])

            command_list = ['eda', self.command_name] + args_no_export + [target]

            util.info(f'export-run: from {export_obj.out_dir=}: {command_list=}')
            self.exec(
                work_dir=export_obj.out_dir,
                command_list=command_list,
            )


    def do_it(self):
        self.prepare_compile()
        self.write_eda_config_and_args()

        if self.is_export_enabled():
            # If we're exporting the target, we do NOT run the test here
            # (do_export() may run the test in a separate process and
            # from the out_dir if --export-run was set)
            self.do_export()
            return self.status

        self.compile()
        self.elaborate()
        self.simulate()

    def set_tool_defines(self):
        pass

    # Methods that derived classes may override:
    def prepare_compile(self):
        self.set_tool_defines()

    def check_logs_for_errors(self, filename:str, bad_strings=[], must_strings=[],
                              use_bad_strings=True, use_must_strings=True):
        _bad_strings = bad_strings
        _must_strings = must_strings
        # append, if not they would 'replace' the args values:
        if use_bad_strings:
            _bad_strings = bad_strings + self.args.get('log-bad-strings', [])
        if use_must_strings:
            _must_strings = must_strings + self.args.get('log-must-strings', [])

        if self.args['pass-pattern'] != "":
            _must_strings.append(self.args['pass-pattern'])

        if len(_bad_strings) > 0 or len(_must_strings) > 0:
            hit_bad_string = False
            hit_must_string_dict = dict.fromkeys(_must_strings)
            fname = os.path.join(self.args['work-dir'], filename)
            with open(fname, "r") as f:
                for iter,line in enumerate(f):
                    if any(must_str in line for must_str in _must_strings):
                        for k in hit_must_string_dict.keys():
                            if k in line:
                                hit_must_string_dict[k] = True
                    if any(bad_str in line for bad_str in _bad_strings):
                        hit_bad_string = True
                        self.error(f"log {fname}:{iter} contains one of {_bad_strings=}")

            if hit_bad_string:
                self.status += 1
            if any(x is None for x in hit_must_string_dict.values()):
                self.error(f"Didn't get all passing patternsin log {fname}: {_must_strings=} {hit_must_string_dict=}")
                self.status += 1

    # Methods that derived classes must override:

    def compile(self):
        raise NotImplementedError

    def elaborate(self):
        raise NotImplementedError

    def simulate(self):
        raise NotImplementedError

    def get_compile_command_lists(self, **kwargs) -> list():
        ''' Returns a list of lists (list of command lists).'''
        raise NotImplementedError

    def get_elaborate_command_lists(self, **kwargs) -> list():
        ''' Returns a list of lists (list of command lists).'''
        raise NotImplementedError

    def get_simulate_command_lists(self, **kwargs) -> list():
        ''' Returns a list of lists (list of command lists).'''
        raise NotImplementedError

    def get_post_simulate_command_lists(self, **kwargs) -> list():
        ''' Returns a list of lists (list of command lists).'''
        raise NotImplementedError



class CommandElab(CommandSim):
    def __init__(self, config:dict):
        CommandSim.__init__(self, config=config)
        self.command_name = 'elab'
        # add args specific to this simulator
        self.args['stop-after-elaborate'] = True
        self.args['lint'] = True
        self.args['verilate-args'] = list()

    def simulate(self):
        pass

    def get_simulate_command_lists(self, **kwargs):
        pass


class CommandSynth(CommandDesign):

    CHECK_REQUIRES = [Tool]
    error_on_no_files_or_targets = True
    error_on_missing_top = True

    def __init__(self, config:dict):
        CommandDesign.__init__(self, config, "synth")
        self.args.update({
            'flatten-all': False,
            'flatten-none':  False,
            'clock-name': 'clock',
            'clock-ns': 5,
            'idelay-ns': 2,
            'odelay-ns': 2,
            'synth-blackbox': list(),
        })
        self.defines['SYNTHESIS'] = None

    def process_tokens(self, tokens, process_all=True):
        CommandDesign.process_tokens(self, tokens, process_all)


        if self.status_any_error():
            return

        # add defines for this job type
        if (self.args['top'] != ""):
            # create our work dir
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()

    def do_export(self):
        from opencos import export_helper

        out_dir = os.path.join(self.args['work-dir'], 'export')

        target = self.target
        if not target:
            target = 'test'

        export_obj = export_helper.ExportHelper( cmd_design_obj=self,
                                                 eda_command=self.command_name,
                                                 out_dir=out_dir,
                                                 # Note this may not be the correct target for debug infomation,
                                                 # so we'll only have the first one.
                                                 target=target )

        # Set things in the exported: DEPS.yml
        tool = self.args.get('tool', None)
        # Certain args are allow-listed here
        deps_file_args = list()
        for a in self.get_command_line_args():
            if any([a.startswith(x) for x in [
                    '--xilinx',
                    '--optimize',
                    '--synth',
                    '--idelay',
                    '--odelay',
                    '--flatten',
                    '--clock',
                    '--yosys']]):
                deps_file_args.append(a)

        export_obj.run(
            deps_file_args=deps_file_args,
            export_json_eda_config={
                'tool': tool,
            }
        )

        if self.args['export-run']:

            # remove the '--export' named args, we don't want those.
            args_no_export = self.get_command_line_args(remove_args_startswith=['export'])

            command_list = ['eda', self.command_name] + args_no_export + [target]

            util.info(f'export-run: from {export_obj.out_dir=}: {command_list=}')
            self.exec(
                work_dir=export_obj.out_dir,
                command_list=command_list,
            )


class CommandProj(CommandDesign):
    def __init__(self, config:dict):
        CommandDesign.__init__(self, config, "proj")

    def process_tokens(self, tokens, process_all=True):
        CommandDesign.process_tokens(self, tokens, process_all)

        if self.status_any_error():
            return

        # add defines for this job type
        if (self.args['top'] != ""):
            # create our work dir
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()

class CommandBuild(CommandDesign):

    CHECK_REQUIRES = [Tool]
    error_on_no_files_or_targets = True
    error_on_missing_top = True

    def __init__(self, config:dict):
        CommandDesign.__init__(self, config, "build")
        self.args['build-script'] = "build.tcl"

    def process_tokens(self, tokens, process_all=True):
        CommandDesign.process_tokens(self, tokens, process_all)

        if self.status_any_error():
            return

        # add defines for this job type
        if (self.args['top'] != ""):
            # create our work dir
            self.create_work_dir()
            self.run_dep_commands()
            self.do_it()

_threads_start = 0
_threads_done = 0

class CommandParallelWorker(threading.Thread):
    def __init__(self, n, work_queue, done_queue):
        threading.Thread.__init__(self)
        self.n = n
        self.work_queue = work_queue
        self.done_queue = done_queue
        self.stop_request = False
        self.job_name = ""
        self.proc = None
        self.pid = None
        self.last_timer_debug = 0
        util.debug(f"WORKER_{n}: START")

    def run(self):
        global _threads_start
        global _threads_done
        while True:
            # Get the work from the queue and expand the tuple
            i, command_list, job_name, work_dir = self.work_queue.get()
            self.job_name = job_name
            try:
                util.debug(f"WORKER_{self.n}: Running job {i}: {job_name}")
                PIPE=subprocess.PIPE
                STDOUT=subprocess.STDOUT
                util.debug(f"WORKER_{self.n}: Calling Popen")
                proc = subprocess.Popen(command_list, stdout=PIPE, stderr=STDOUT)
                self.proc = proc
                util.debug(f"WORKER_{self.n}: Opened process, PID={proc.pid}")
                self.pid = proc.pid
                _threads_start += 1
                while proc.returncode == None:
                    try:
                        if (time.time() - self.last_timer_debug) > 10:
                            util.debug(f"WORKER_{self.n}: Calling proc.communicate")
                        stdout, stderr = proc.communicate(timeout=0.5)
                        util.debug(f"WORKER_{self.n}: got: \n*** stdout:\n{stdout}\n*** stderr:{stderr}")
                    except subprocess.TimeoutExpired:
                        if (time.time() - self.last_timer_debug) > 10:
                            util.debug(f"WORKER_{self.n}: Timer expired, stop_request={self.stop_request}")
                            self.last_timer_debug = time.time()
                        pass
                    if self.stop_request:
                        util.debug(f"WORKER_{self.n}: got stop request, issuing SIGINT")
                        proc.send_signal(signal.SIGINT)
                        util.debug(f"WORKER_{self.n}: got stop request, calling proc.wait")
                        proc.wait()
                    if False and self.stop_request:
                        util.debug(f"WORKER_{self.n}: got stop request, issuing proc.terminate")
                        proc.terminate()
                        util.debug(f"WORKER_{self.n}: proc poll returns is now {proc.poll()}")
                        try:
                            util.debug(f"WORKER_{self.n}: Calling proc.communicate")
                            stdout, stderr = proc.communicate(timeout=0.2) # for completeness, in case we ever pipe/search stdout/stderr
                            util.debug(f"WORKER_{self.n}: got: \n*** stdout:\n{stdout}\n*** stderr:{stderr}")
                        except subprocess.TimeoutExpired:
                            util.debug(f"WORKER_{self.n}: timeout waiting for comminicate after terminate")
                        except:
                            pass
                        util.debug(f"WORKER_{self.n}: proc poll returns is now {proc.poll()}")

                util.debug(f"WORKER_{self.n}: -- out of while loop")
                self.pid = None
                self.proc = None
                self.job_name = "<idle>"
                util.debug(f"WORKER_{self.n}: proc poll returns is now {proc.poll()}")
                try:
                    util.debug(f"WORKER_{self.n}: Calling proc.communicate one last time")
                    stdout, stderr = proc.communicate(timeout=0.1) # for completeness, in case we ever pipe/search stdout/stderr
                    util.debug(f"WORKER_{self.n}: got: \n*** stdout:\n{stdout}\n*** stderr:{stderr}")
                except subprocess.TimeoutExpired:
                    util.debug(f"WORKER_{self.n}: timeout waiting for communicate after loop?")
                except:
                    pass
                return_code = proc.poll()
                util.debug(f"WORKER_{self.n}: Finished job {i}: {job_name} with return code {return_code}")
                self.done_queue.put((i, job_name, return_code))
            finally:
                util.debug(f"WORKER_{self.n}: -- in finally block")
                self.work_queue.task_done()
                _threads_done += 1


class CommandParallel(Command):
    def __init__(self, config, command_name):
        Command.__init__(self, config, command_name)
        self.jobs = list()
        self.jobs_status = list()
        self.args['parallel'] = 1
        self.worker_threads = list()

    def __del__(self):
        util.debug(f"In Command.__del__, threads done/started: {_threads_done}/{_threads_start}")
        if _threads_start == _threads_done:
            return
        util.warning(f"Need to shut down {_threads_start-_threads_done} worker threads...")
        for w in self.worker_threads:
            if w.proc:
                util.warning(f"Requesting stop of PID {w.pid}: {w.job_name}")
                w.stop_request = True
        for i in range(10):
            util.debug(f"Threads done/started: {_threads_done}/{_threads_start}")
            if _threads_start == _threads_done:
                util.info(f"All threads done")
                return
            time.sleep(1)
        subprocess.Popen(['stty', 'sane']).wait()
        util.debug(f"Scanning workers again")
        for w in self.worker_threads:
            if w.proc:
                util.info(f"need to SIGINT WORKER_{w.n}, may need manual cleanup, check 'ps'")
                if w.pid:
                    os.kill(w.pid, signal.SIGINT)
        for i in range(5):
            util.debug(f"Threads done/started: {_threads_done}/{_threads_start}")
            if _threads_start == _threads_done:
                util.info(f"All threads done")
                return
            time.sleep(1)
        subprocess.Popen(['stty', 'sane']).wait()
        util.debug(f"Scanning workers again")
        for w in self.worker_threads:
            if w.proc:
                util.info(f"need to TERM WORKER_{w.n}, probably needs manual cleanup, check 'ps'")
                if w.pid:
                    os.kill(w.pid, signal.SIGTERM)
        for i in range(5):
            util.debug(f"Threads done/started: {_threads_done}/{_threads_start}")
            if _threads_start == _threads_done:
                util.info(f"All threads done")
                return
            time.sleep(1)
        subprocess.Popen(['stty', 'sane']).wait()
        util.debug(f"Scanning workers again")
        for w in self.worker_threads:
            if w.proc:
                util.info(f"need to KILL WORKER_{w.n}, probably needs manual cleanup, check 'ps'")
                if w.pid:
                    os.kill(w.pid, signal.SIGKILL)
        util.stop_log()
        subprocess.Popen(['stty', 'sane']).wait()

    def run_jobs(self, command):
        # this is where we actually run the jobs.  it's a messy piece of code and prob could use refactoring
        # but the goal was to share as much as possible (job start, end, pass/fail judgement, etc) while
        # supporting various mode combinations (parallel mode, verbose mode, fancy mode, etc) and keeping the
        # UI output functional and awesome sauce

        # walk targets to find the longest name, for display reasons
        longest_job_name = 0
        total_jobs = len(self.jobs)
        self.jobs_status = [None] * total_jobs
        for i in range(total_jobs):
            l = len(self.jobs[i]['name'])
            if l>longest_job_name: longest_job_name = l

        run_parallel = self.args['parallel'] > 1

        # figure out the width to print various numbers
        jobs_digits = len(f"{total_jobs}")
        jobs_fmt = "%%%dd" % jobs_digits # ugh, for printing out a number with N digits

        # run the jobs!
        running_jobs = {}
        passed_jobs = []
        failed_jobs = []
        workers = []
        jobs_complete = 0
        jobs_launched = 0
        num_parallel = min(len(self.jobs), self.args['parallel'])
        # 16 should really be the size of window or ?
        (columns,lines) = shutil.get_terminal_size()
        # we will enter fancy mode if we are parallel and we can leave 6 lines of regular scrolling output
        fancy_mode = util.args['fancy'] and (num_parallel > 1) and (num_parallel <= (lines-6))
        multi_cwd = util.getcwd() + os.sep

        if run_parallel:
            # we are doing this multi-threaded
            util.info(f"Parallel: Running multi-threaded, starting {num_parallel} workers")
            work_queue = queue.Queue()
            done_queue = queue.Queue()
            for x in range(num_parallel):
                worker = CommandParallelWorker(x, work_queue, done_queue)
                # Setting daemon to True will let the main thread exit even though the workers are blocking
                worker.daemon = True
                worker.start()
                self.worker_threads.append(worker)
                workers.append(x)
            if fancy_mode:
                # in fancy mode, we will take the bottom num_parallel lines to show state of workers
                util.fancy_start(fancy_lines=num_parallel)
                for x in range(num_parallel):
                    util.fancy_print(f"Starting worker {x}", x)

        while len(self.jobs) or len(running_jobs.items()):
            job_done = False
            job_done_quiet = False
            anything_done = False

            def sprint_job_line(job_number=0, job_name="", final=False, hide_stats=False):
                return (f"INFO: [EDA] " +
                        util.string_or_space(f"[job {jobs_fmt%job_number}/{jobs_fmt%total_jobs} ", final) +
                        util.string_or_space(f"| pass ", hide_stats or final) +
                        util.string_or_space(f"{jobs_fmt%len(passed_jobs)}/{jobs_fmt%jobs_complete} ", hide_stats) +
                        util.string_or_space(f"@ {(100*(jobs_complete))/total_jobs:5.1f}%", hide_stats or final) +
                        util.string_or_space(f"] ", final) +
                        f"{command} {(job_name+' ').ljust(longest_job_name+3,'.')}")

            # for any kind of run (parallel or not, fancy or not, verbose or not) ... can we launch a job?
            if len(self.jobs) and (len(running_jobs.items()) < num_parallel):
                # we are launching a job
                jobs_launched += 1
                anything_done = True
                job = self.jobs.pop(0)
                if job['name'].startswith(multi_cwd): job['name'] = job['name'][len(multi_cwd):]
                # in all but fancy mode, we will print this text at the launch of a job.  It may get a newline below
                job_text = sprint_job_line(jobs_launched, job['name'], hide_stats=run_parallel)
                command_list = job['command_list']
                cwd = util.getcwd()

                if run_parallel:
                    # multithreaded job launch: add to queue
                    worker = workers.pop(0) # we don't actually know which thread will pick up, but GUI will be consistent
                    running_jobs[str(jobs_launched)] = { 'name' : job['name'],
                                                         'number' : jobs_launched,
                                                         'worker' : worker,
                                                         'start_time' : time.time(),
                                                         'update_time' : time.time()}
                    work_queue.put((jobs_launched, command_list, job['name'], cwd))
                    suffix = "<START>"
                    if fancy_mode:
                        util.fancy_print(job_text+suffix, worker)
                    else:
                        # if we aren't in fancy mode, we will print a START line, periodic RUNNING lines, and PASS/FAIL line per-job
                        if len(failed_jobs): util.print_orange(job_text + util.string_yellow + suffix)
                        else:                util.print_yellow(job_text + util.string_yellow + suffix)
                else:
                    # single-threaded job launch, we are going to print out job info as we start each job... no newline
                    # since non-verbose silences the job and prints only <PASS>/<FAIL> after the trailing "..." we leave here
                    if len(failed_jobs): util.print_orange(job_text, end="")
                    else:                util.print_yellow(job_text, end="")
                    job_done_number = jobs_launched
                    job_done_name = job['name']
                    job_start_time = time.time()
                    if util.args['verbose']:
                        # previous status line gets a \n, then job is run passing
                        # stdout/err, then print 'job_text' again with pass/fail
                        util.print_green("")
                        # run job, sending output to the console
                        _, _, job_done_return_code = self.exec(
                            cwd, command_list, background=False, stop_on_error=False, quiet=False
                        )
                        # reprint the job text previously printed before running job(and given "\n" after the trailing "...")
                    else:
                        # run job, swallowing output (hope you have a logfile)
                        _, _, job_done_return_code = self.exec(
                            cwd, command_list, background=True, stop_on_error=False, quiet=True
                        )
                        job_done_quiet = True # in this case, we have the job start text (trailing "...", no newline) printed
                    job_done = True
                    job_done_run_time = time.time() - job_start_time
                    # Since we consumed the job, use the job['index'] to track the per-job status:

            if run_parallel:
                # parallel run, check for completed job
                if done_queue.qsize():
                    # we're collecting a finished job from a worker thread.  note we will only reap one job per iter of the big
                    # loop, so as to share job completion code at the bottom
                    anything_done = True
                    job_done = True
                    job_done_number, job_done_name, job_done_return_code = done_queue.get()
                    t = running_jobs[str(job_done_number)]
                    # in fancy mode, we need to clear the worker line related to this job.
                    if fancy_mode:
                        util.fancy_print(f"INFO: [EDA] Parallel: Worker Idle ...", t['worker'])
                    job_done_run_time = time.time() - t['start_time']
                    util.debug(f"removing job #{job_done_number} from running jobs")
                    del running_jobs[str(job_done_number)]
                    workers.append(t['worker'])

            if run_parallel:
                # parallel run, update the UI on job status
                for _,t in running_jobs.items():
                    if (fancy_mode or (time.time() - t['update_time']) > 30):
                        t['update_time'] = time.time()
                        job_text = sprint_job_line(t['number'], t['name'], hide_stats=True)
                        suffix = f"<RUNNING: {util.sprint_time(time.time() - t['start_time'])}>"
                        if fancy_mode:
                            util.fancy_print(f"{job_text}{suffix}", t['worker'])
                        else:
                            if len(failed_jobs): util.print_orange(job_text+util.string_yellow+suffix)
                            else:                util.print_yellow(job_text+util.string_yellow+suffix)

            # shared job completion code
            # single or multi-threaded, we can arrive here to harvest <= 1 jobs, and need {job, return_code} valid, and
            # we expect the start of a status line to have been printed, ready for pass/fail
            if job_done:
                jobs_complete += 1
                if job_done_return_code is None or job_done_return_code:
                    # embed the color code, to change color of pass/fail during the util.print_orange/yellow below
                    if job_done_return_code == 124:
                        # bash uses 124 for bash timeout errors, if that was preprended to the command list.
                        suffix = f"{util.string_red}<TOUT: {util.sprint_time(job_done_run_time)}>"
                    else:
                        suffix = f"{util.string_red}<FAIL: {util.sprint_time(job_done_run_time)}>"
                    failed_jobs.append(job_done_name)
                else:
                    suffix = f"{util.string_green}<PASS: {util.sprint_time(job_done_run_time)}>"
                    passed_jobs.append(job_done_name)
                # we want to print in one shot, because in fancy modes that's all that we're allowed
                job_done_text = "" if job_done_quiet else sprint_job_line(job_done_number, job_done_name)
                if len(failed_jobs): util.print_orange(f"{job_done_text}{suffix}")
                else:                util.print_yellow(f"{job_done_text}{suffix}")
                self.jobs_status[job_done_number-1] = job_done_return_code

            if not anything_done:
                time.sleep(0.25) # if nothing happens for an iteration, chill out a bit

        if total_jobs:
            emoji = "< :) >" if (len(passed_jobs) == total_jobs) else "< :( >"
            util.info(sprint_job_line(final=True,job_name="jobs passed")+emoji, start="")
        else:
            util.info(f"Parallel: <No jobs found>")
        # Make sure all jobs have a set status:
        for iter,rc in enumerate(self.jobs_status):
            if rc is None or type(rc) != int:
                self.error(f'job {iter=} {rc=} did not return a proper return code')
                jobs_status[iter] = 1

        # if self.status > 0, then keep it non-zero, else set it if we still have running jobs.
        if self.status == 0:
            self.status = 0 if len(self.jobs_status) == 0 else max(self.jobs_status)
        util.fancy_stop()


class CommandMulti(CommandParallel):
    def __init__(self, config:dict):
        CommandParallel.__init__(self, config, "multi")
        self.args.update({
            'single-timeout': None, # timeout on a single operation in multi, not the entire multi command.
            'fail-if-no-targets': False,
            'export-jsonl': False, # generates export.jsonl if possible, spawns single commands with --export-json
        })
        self.single_command = ''
        self.targets = list() # list of tuples (target:str, tool:str)

    def resolve_target(self, base_path, target, command, level=0):
        util.debug(f"ENTER RESOLVE_TARGET L{level} base_path={base_path}, target={target}, command={command}")
        target = target.strip('"').strip("'")
        target_path_parts = target.split("/")
        all_multi_tools = self.multi_which_tools(command)
        if len(target_path_parts) == 1:
            util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, {target} is a single-part target, look for matches in here")

            target_pattern = "^"+target_path_parts.pop(0)+"$"
            target_pattern = target_pattern.replace("*", r"[^\/]*")
            util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, target_pattern={target_pattern}")

            deps_file = get_deps_markup_file(base_path)
            if self.config['deps_markup_supported'] and deps_file:
                data = deps_markup_safe_load(deps_file)

                if data is not None:
                    deps_file_defaults = data.get('DEFAULTS', dict())

                    # Loop through all the targets in DEPS.yml, skipping DEFAULTS
                    for target_node, entry in data.items():

                        # Skip upper-case targets, including 'DEFAULTS':
                        if target_node == target_node.upper():
                            continue

                        m = re.match(target_pattern, target_node)
                        if not m:
                            # If the target_node in our deps_file doesn't match the pattern then skip.
                            continue

                        # Since we support a few schema flavors for a target (our 'target_node' key in a DEPS.yml file),
                        # santize the entry so it's a dict() with a 'deps' key:
                        entry_sanitized = deps_helpers.deps_list_target_sanitize(entry, target_node=target_node, deps_file=deps_file)

                        # Start with the defaults, and override with this entry_sanitized
                        entry_with_defaults = deps_file_defaults.copy()
                        entry_with_defaults.update(entry_sanitized)
                        entry = entry_with_defaults

                        # Because CommandMulti has child CommandToolsMulti, we support multiple tools
                        # and have multi ignore waivers tha may only be some of those tools. Keep a list
                        # of tools we skip for this target.
                        multi_ignore_skip_this_target_node = set() # which tools we'll skip

                        # Check if this target_node should be skipped due to multi - ignore-this-target (commands or tools)
                        multi_ignore_commands_list = entry.get('multi', dict()).get('ignore-this-target', list())
                        for x in multi_ignore_commands_list:
                            if len(multi_ignore_skip_this_target_node) == len(all_multi_tools):
                                # If we already found a reason to not use this target due to multi - ignore,
                                # on all tools, then stop.
                                break

                            assert type(x) is dict, \
                                f'multi ignore-this-target: {x=} {multi_ignore_commands_list=} {deps_file_defaults=}' \
                                + f'  This needs to be a dict() entry with keys "commands" and "tools" {deps_file=} {target_node=}'

                            commands = x.get('commands', list())
                            tools = x.get('tools', list())
                            ignore_commands_list = deps_helpers.dep_str2list(commands)
                            ignore_tools_list = deps_helpers.dep_str2list(tools)

                            util.debug(f"RESOLVE_TARGET L{level}: {ignore_tools_list=}, {ignore_commands_list=} {target_node=}")
                            util.debug(f"RESOLVE_TARGET L{level}: {command=} --> {all_multi_tools=}")
                            if command in ignore_commands_list or ignore_commands_list == ['None'] or \
                               len(ignore_commands_list) == 0:
                                # if commands: None, or commands is blank, then assume it is all commands.
                                # (note that yaml doesn't support *)

                                for tool in all_multi_tools:
                                    if tool in ignore_tools_list or ignore_tools_list == ['None'] or \
                                       len(ignore_tools_list) == 0:
                                        # if tools: None, or tools is blank, then assume it is for all tools
                                        util.debug(f"RESOLVE_TARGET L{level}: Skipping {target_node=}",
                                                   f" due to using {command=} {tool=}",
                                                   f" given {ignore_tools_list=} and {ignore_commands_list=}")
                                        multi_ignore_skip_this_target_node.add(tool)

                        for tool in all_multi_tools:
                            if tool not in multi_ignore_skip_this_target_node:
                                util.debug(f"RESOLVE_TARGET L{level}: Found dep {target_node=} {tool=} matching {target_pattern=} {entry=}")
                                self.targets.append( tuple([os.path.join(base_path, target_node), tool]) )

        else:
            # let's look at the first part of the multi-part target path, which should be a dir
            part = target_path_parts.pop(0)
            if part == ".":
                # just reprocess this directory (matches "./some/path" and retries as "some/path")
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, recursing here")
                self.resolve_target(base_path, os.path.sep.join(target_path_parts), command, level+1)
            elif part == "..":
                # reprocess from the directory above (../some/path --> change base_path, some/path)
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, recursing above at ../")
                new_base_path = os.path.abspath(os.path.join(base_path, part))
                self.resolve_target(new_base_path, os.path.sep.join(target_path_parts),
                                    command, level+1)
            elif part == "...":
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, recursing to check here")
                # first we check this dir: {"<base>",".../target"} should match "target" in <base>, so we call {"<base>","target"}
                self.resolve_target(base_path, os.path.sep.join(target_path_parts), command, level+1)
                # now we find all dirs in <base> ...
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, looking through dirs...")
                wtg = os.listdir(base_path)
                for e in os.listdir(base_path):
                    util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path},e={e},isdir={os.path.isdir(os.path.join(base_path,e))}")
                    if e == 'eda.work' or e == self.args['eda-dir']:
                        util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, skipping work dir {e}")
                    elif os.path.islink(os.path.join(base_path,e)):
                        util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, skipping link dir {e}")
                    elif os.path.isdir(os.path.join(base_path,e)):
                        util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, recursing into {e}")
                        self.resolve_target(os.path.join(base_path,e), target, command, level+1)
            elif part.startswith("."):
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, skipping hidden")
            elif part == self.args['eda-dir']:
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, skipping eda.dir")
            elif os.path.isdir(os.path.join(base_path, part)):
                # reprocess in a lower directory (matches "some/...", enters "some/", and retries "...")
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, recursing down")
                self.resolve_target(os.path.join(base_path, part), os.path.sep.join(target_path_parts), command, level+1)
            elif part == "*":
                # descend into every directory, we only go in if there's a DEPS though
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part}, looking through dirs...")
                for e in os.listdir(base_path):
                    util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path},e={e}")
                    if os.path.isdir(e):
                        util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path},looking for ={os.path.join(base_path,e,'DEPS')}")
                        deps_markup_file = get_deps_markup_file(os.path.join(base_path, e))
                        if (self.config['deps_markup_supported'] and deps_markup_file):
                            self.resolve_target(os.path.join(base_path, e),
                                                os.path.sep.join(target_path_parts), command, level+1)
            else:
                util.debug(f"RESOLVE_TARGET L{level}: base_path={base_path}, processing {part} ... but not sure what to do with it?")

    def get_argparser(self) -> argparse.ArgumentParser:
        ''' Returns an argparse.ArgumentParser() for CommandMulti (not based on on self.args (dict))'''
        parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        bool_action_kwargs = util.get_argparse_bool_action_kwargs()
        parser.add_argument('--fake',     **bool_action_kwargs)
        parser.add_argument('--parallel', default=1, type=int)
        parser.add_argument('--single-timeout',  default=None,
                            help='set for a single job (within multi) timeout in seconds')
        parser.add_argument('--export-jsonl', **bool_action_kwargs)
        parser.add_argument('--fail-if-no-targets', action='store_true',  # don't support --no-(foo) on this arg.
                            help='set if you want `eda multi` to fail if no globbed targets found')
        return parser


    def process_tokens(self, tokens, process_all=True):
        # multi is special in the way it handles tokens, due to most of them being processed by
        # a subprocess to another eda.Command class (for the command)
        arg_tokens = [] # these are the tokens we will pass to the child eda processes
        command = ""
        target_globs = []
        parallelism = 1
        tool = None
        orig_tokens = tokens.copy()

        parser = self.get_argparser()

        try:
            parsed, unparsed = parser.parse_known_args(tokens + [''])
            unparsed = list(filter(None, unparsed))
        except argparse.ArgumentError:
            self.error(f'problem attempting to parse_known_args for {tokens=}')

        for key,value in vars(parsed).items():
            if key not in self.args and '_' in key:
                # try with dashes instead of _
                key = key.replace('_', '-')
            if value is None:
                continue
            self.args[key] = value # set fake, parallel, and fail_if_no_targets.
        if parsed.parallel < 1 or parsed.parallel > 256:
            self.error("Arg 'parallel' must be between 1 and 256")

        for value in unparsed:
            if value in self.config['command_handler'].keys():
                command = value
                unparsed.remove(value)
                break

        # Need to know the tool for this command, either it was set correctly via --tool and/or
        # the command (class) will tell us.
        all_multi_tools = self.multi_which_tools(command)

        util.debug(f"Multi: {unparsed=}, looking for target_globs")
        for token in unparsed:
            if token.startswith("-") or token.startswith("+"):
                # save all --arg, -arg, or +plusarg for the job target:
                arg_tokens.append(token)
            else:
                target_globs.append(token)

        if command == "": self.error(f"Didn't get a command after 'multi'!")

        # now we need to expand the target list
        self.single_command = command
        util.debug(f"Multi: {orig_tokens=}")
        util.debug(f"Multi: {command=}")
        util.debug(f"Multi: {self.config=}")
        util.debug(f"Multi: {all_multi_tools=}")
        util.debug(f"Multi: {target_globs=}")
        util.debug(f"Multi: {arg_tokens=}")
        if self.args.get('export-jsonl', False):
            util.info("Multi: --export-jsonl")
        self.targets = list()
        cwd = util.getcwd()
        current_targets = 0
        for t in target_globs:
            self.resolve_target(cwd, t, command)
            if len(self.targets) == current_targets:
                # we didn't get any new targets, try globbing this one
                for f in glob.glob(t):
                    if os.path.isfile(f):
                        util.info(f"Adding raw file target: {f} for tools {all_multi_tools}")
                        for tool in all_multi_tools:
                            self.targets.append( tuple([f, tool]) )
            current_targest = len(self.targets)
        util.info(f"Multi: Expanded {target_globs} to {len(self.targets)} {command} targets")

        if parsed.fail_if_no_targets and len(self.targets) == 0:
            self.error(f'Multi: --fail-if-no-targets set, and {self.targets=}')
        util.info(f"Multi: About to run: ", end="")

        def get_pretty_targets_tuple_as_list(l:list):
            # prints 'a(b)', used for 'target(tool)' for tuples in self.targets
            if len(all_multi_tools) > 1:
                return [f'{a.split("/")[-1]}({b})' for a,b in l]
            else:
                # don't add the (tool) part if we're only running 1 tool
                return [f'{a.split("/")[-1]}' for a,b in l]

        if len(self.targets) > 20:
            mylist = get_pretty_targets_tuple_as_list(self.targets[:10])
            util.info( ", ".join(mylist), start="", end="")
            util.info(f", ... ", start="", end="")
            mylist = get_pretty_targets_tuple_as_list(self.targets[-10:])
            util.info( ", ".join(mylist), start="")
        else:
            mylist = get_pretty_targets_tuple_as_list(self.targets)
            util.info( ", ".join(mylist), start="")

        util.debug(f"Multi: converting list of targets into list of jobs")
        self.jobs = []
        self.append_jobs_from_targets(args=arg_tokens)
        self.run_jobs(command)

        # Because CommandMulti has a custom arg parsing, we do not have 'export' related
        # args in self.args (they are left as 'unparsed' for the glob'ed commands)
        # Note that --export-jsonl has already been removed from 'unparsed' and is in parsed,
        # and would already be set in self.args.
        bool_action_kwargs = util.get_argparse_bool_action_kwargs()
        export_parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        for arg,v in self.args.items():
            if arg.startswith('export') and type(v) is bool:
                export_parser.add_argument(f'--{arg}', **bool_action_kwargs)
        try:
            export_parsed, export_unparsed = export_parser.parse_known_args(unparsed + [''])
            unparsed = list(filter(None, export_unparsed))
        except argparse.ArgumentError:
            self.error(f'problem attempting to parse_known_args for {unparsed=}')

        for key,value in vars(export_parsed).items():
            if key not in self.args and '_' in key:
                # try with dashes instead of _
                key = key.replace('_', '-')
            if value is None:
                continue
            self.args[key] = value # set one of the parsed 'export' args
            util.info(f'Export: setting arg {key}={value}')

        if self.is_export_enabled():
            self.do_export()

    def which_tool(self, command):
        # Do not use for CommandMulti, b/c we support list of tools.
        raise NotImplementedError

    def multi_which_tools(self, command):
        '''returns a list, or None, of the tool that was already determined to run the command

        CommandToolsMulti will override and return its own list'''
        return [which_tool(command, config=self.config)]

    def append_jobs_from_targets(self, args:list):
        eda_path = get_eda_exec('multi')
        command = self.single_command
        timeout = shutil.which('timeout')

        # Built-in support for running > 1 tool.
        all_multi_tools = self.multi_which_tools(command)
        util.info(f'Multi - append_jobs_from_targets: {command=} {all_multi_tools=}')


        for target, tool in self.targets:
            command_list = [ eda_path, command ]

            assert target, f'{target=} {tool=}'

            _, short_target = os.path.split(target) # trim path info on left

            # Many args were consumed by eda before CommandMulti saw them
            # --config-yml, --tool, --eda-safe. Some are in self.config.
            # We need to apply those eda level args to each multi exec-command
            # TODO(drew): this is really clunky. It would be way eaiser if our
            # self.config['eda_original_args'] had a better way of passing allow-listed
            # args from multi --> exec-command.
            # Alternatively, we could track all the parsed args up to this point, that have
            # deviated from the default value(s), and apply those as needed.
            if any([a.startswith('--config-yml') for a in self.config['eda_original_args']]):
                cfg_yml_fname = self.config.get('config-yml', None)
                if cfg_yml_fname:
                    command_list.append(f'--config-yml={cfg_yml_fname}')
            if '--eda-safe' in self.config['eda_original_args']:
                command_list.append('--eda-safe')

            if tool:
                # tool can be None, we won't add it to the command (assumes default from config-yml)
                command_list.append('--tool=' + tool)
                if len(all_multi_tools) > 1:
                    command_list += [f'--sub-work-dir={short_target}.{command}.{tool}']

            if self.args.get('export-jsonl', False):
                # Special case for 'multi' --export-jsonl, run reach child with --export-json
                command_list += [ '--export-json']
            # if self.args['parallel']: command_list += ['--quiet']
            command_list += args # put the args prior to the target.
            command_list += [target]

            # prepend a nix-style 'timeout <seconds>' on the command_list if this was set:
            if timeout and \
               self.args.get('single-timeout', None) and \
               type(self.args['single-timeout']) in [int, str]:
                command_list = ['timeout', str(self.args['single-timeout'])] + command_list

            name = target
            if tool and len(all_multi_tools) > 1:
                name = f'{short_target} ({tool})'

            this_job_dict = {
                'name' : name,
                'index' : len(self.jobs),
                'command_list' : command_list
            }
            if tool:
                util.debug(f'Multi: append_jobs_from_targets: {tool=} {this_job_dict=}')
            else:
                util.debug(f'Multi: append_jobs_from_targets: {this_job_dict=}')
            self.jobs.append(this_job_dict)

    def do_export(self):
        if self.args.get('work-dir', '') == '':
            self.args['work-dir'] = 'eda.work'

        util.info(f'Multi export: One of the --export[..] flag set, may examine {self.args["work-dir"]=}')
        self.collect_single_exported_export_jsonl()
        util.info('Mulit export: done')

    def collect_single_exported_export_jsonl(self) -> None:
        from opencos import export_helper

        do_as_jsonl = self.args.get('export-jsonl', False)
        do_as_json = self.args.get('export-json', False)

        if not do_as_json and not do_as_jsonl:
            return

        if do_as_jsonl:
            outfile_str = 'export.jsonl'
        else:
            outfile_str = 'export.json'

        command = self.single_command
        all_multi_tools = self.multi_which_tools(command)

        json_file_paths = list()
        for target, tool in self.targets:
            # Rather than glob out ALL the possible exported files in our work-dir,
            # only look at the multi targets:
            p, target_nopath = os.path.split(target)
            if not target_nopath:
               target_nopath = p # in case self.targets was missing path info

            if len(all_multi_tools) > 1:
                # Need to look in eda.work/<shorttarget>.<command>.<tool>/export/export.json
                # If this was 'eda export' command, then need to look in eda.export/......./export.json.
                single_pathname = os.path.join(self.args['work-dir'],
                                               f'{target_nopath}.{self.single_command}.{tool}',
                                               'export', 'export.json')
            else:
                # We only ran for 1 tool, so the tool value is a dontcare in the output path
                # Need to look in eda.work/<shorttarget>.<command>/export/export.json
                single_pathname = os.path.join(self.args['work-dir'],
                                               f'{target_nopath}.{self.single_command}',
                                               'export', 'export.json')
            util.debug(f'Looking for export.json in: {single_pathname=}')
            if os.path.exists(single_pathname):
                json_file_paths.append(single_pathname)


        output_json_path = os.path.join(self.args['work-dir'], 'export', outfile_str)
        if len(json_file_paths) == 0:
            self.error(f'{json_file_paths=} is empty list, no targets found to export for {output_json_path=}')
            return

        # TODO(drew): If we ran this w/ several tools from CommandToolsMulti, we'll end up
        # with tests having same name (but different tool). Might need to uniquify the names.
        util.debug(f'Multi export: {json_file_paths=}')
        if do_as_jsonl:
            util.info(f'Multi export: saving JSONL format to: {output_json_path=}')
            export_helper.json_paths_to_jsonl(json_file_paths=json_file_paths,
                                              output_json_path=output_json_path)
        else:
            util.info('Multi export: saving JSON format to: {output_json_path=}')
            export_helper.json_paths_to_single_json(json_file_paths=json_file_paths,
                                                    output_json_path=output_json_path)


class CommandToolsMulti(CommandMulti):

    def __init__(self, config:dict):
        super().__init__(config)
        self.all_handler_commands = dict() # cmd: [ordered list of tools]
        self.tools = set()
        self.args.update({
            'tools': list(), # Used for help, will internally use self.tools from argparser.
        })
        self.args_help.update({
            'tools': 'list of tools to run for eda multi targets, such as' \
            + ' --tools=modelsim_ase --tools=verilator=/path/to/bin/verilator',
        })
        if 'tool' in self.args:
            self.args.pop('tool')

        self.update_all_known_tools()

    def update_all_known_tools(self):
        from opencos import eda_tool_helper
        cfg, tools_loaded = eda_tool_helper.get_config_and_tools_loaded(quiet=True)
        self.all_handler_commands = eda_tool_helper.get_all_handler_commands(cfg, tools_loaded)
        util.debug(f'CommandToolsMulti: {self.all_handler_commands=}')

    def multi_which_tools(self, command):
        '''Overrides CommandMulti.multi_which_tool(command), return a list of all
        possible tools that can run this command'''
        if self.tools is None or len(self.tools) == 0:
            # wasn't set via arg --tools, so use all if possible for this command.
            which_tools = self.all_handler_commands.get(command, list())
        else:
            # self.tools set from args --tools (list)
            which_tools = [tool for tool in self.all_handler_commands.get(command, list()) \
                           if tool in self.tools]
        return which_tools

    def process_tokens(self, tokens, process_all=True):

        # setup an argparser to append tools to a list, if no tools set, then use
        # all possible tools.
        parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        parser.add_argument('--tools', default=list(), action='append')
        try:
            parsed, unparsed = parser.parse_known_args(tokens + [''])
            unparsed = list(filter(None, unparsed))
        except argparse.ArgumentError:
            self.error(f'CommandToolsMulti: problem attempting to parse_known_args for {tokens=}')

        if len(parsed.tools) == 0:
            self.tools = set()
        else:
            # deal with --tools=name=/path/to/name (update config w/ path info):
            self.tools = set(
                eda_config.update_config_auto_tool_order_for_tools(
                    tools=parsed.tools, config=self.config
                )
            )
            util.info(f'CommandToolsMulti: {self.tools=}')
        self.args['tools'] = self.tools

        # Call ComamndMulti's process_tokens:
        super().process_tokens(unparsed, process_all)


class CommandSweep(CommandDesign, CommandParallel):
    def __init__(self, config:dict):
        CommandDesign.__init__(self, config, "sweep")
        CommandParallel.__init__(self, config, "sweep")

    def process_tokens(self, tokens, process_all=True):
        # multi is special in the way it handles tokens, due to most of them being processed by a sub instance
        sweep_axis_list = []
        command = ""
        target = ""
        arg_tokens = []

        parser = argparse.ArgumentParser(prog='eda', add_help=False, allow_abbrev=False)
        parser.add_argument('--parallel', default=1, type=int)
        try:
            parsed, unparsed = parser.parse_known_args(tokens + [''])
            unparsed = list(filter(None, unparsed))
        except argparse.ArgumentError:
            self.error(f'problem attempting to parse_known_args for {tokens=}')
        for k,v in vars(parsed).items():
            self.args[k] = v # set parallel.
        if self.args['parallel'] < 1 or self.args['parallel'] > 256:
            self.error("Arg 'parallel' must be between 1 and 256")

        for value in unparsed:
            if value in self.config['command_handler'].keys():
                command = value
                unparsed.remove(value)
                break

        tokens = unparsed

        # TODO(drew): similar clunky behavior with self.config['eda_orignal_args'] that CommandMulti has
        # we need to pass global args to each sweep job, which we can do via arg_tokens (list)
        # TODO(drew): fix this, for now it works but --color and other args do not work.
        if any([a.startswith('--config-yml') for a in self.config['eda_original_args']]):
            cfg_yml_fname = self.config.get('config-yml', None)
            if cfg_yml_fname:
                arg_tokens.append(f'--config-yml={cfg_yml_fname}')
        if '--eda-safe' in self.config['eda_original_args']:
            arg_tokens.append('--eda-safe')
        if any([a.startswith('--tool') for a in self.config['eda_original_args']]):
            tool = self.config.get('tool', None)
            if tool:
                arg_tokens.append('--tool=' + tool)


        while len(tokens):
            token = tokens.pop(0)

            # command and --parallel already processed by argparse

            m = re.match(r'(\S+)\=\(([\d\.]+)\,([\d\.]+)(,([\d\.]+))?\)', token)
            if m:
                sweep_axis = { 'key' : m.group(1),
                               'values' : [  ] }
                for v in range(float(m.group(2)), (float(m.group(3))+1), (float(m.group(5)) if m.group(4) != None else 1.0)):
                    sweep_axis['values'].append(v)
                util.debug(f"Sweep axis: {sweep_axis['key']} : {sweep_axis['values']}")
                sweep_axis_list.append(sweep_axis)
                continue
            m = re.match(r'(\S+)\=\[([^\]]+)\]', token)
            if m:
                sweep_axis = { 'key' : m.group(1), 'values' : [] }
                for v in m.group(2).split(','):
                    v = v.replace(' ','')
                    sweep_axis['values'].append(v)
                util.debug(f"Sweep axis: {sweep_axis['key']} : {sweep_axis['values']}")
                sweep_axis_list.append(sweep_axis)
                continue
            if token.startswith('--') or token.startswith('+'):
                arg_tokens.append(token)
                continue
            if self.resolve_target(token, no_recursion=True):
                if target != "":
                    self.error(f"Sweep can only take one target, already got {target}, now getting {token}")
                target = token
                continue
            self.error(f"Sweep doesn't know what to do with arg '{token}'")
        if command == "": self.error(f"Didn't get a command after 'sweep'!")

        # now we need to expand the target list
        util.debug(f"Sweep: command:    '{command}'")
        util.debug(f"Sweep: arg_tokens: '{arg_tokens}'")
        util.debug(f"Sweep: target:     '{target}'")

        # now create the list of jobs, support one axis
        self.jobs = []
        self.expand_sweep_axis(command, target, arg_tokens, sweep_axis_list)
        return self.run_jobs(command)

    def expand_sweep_axis(self, command, target, arg_tokens, sweep_axis_list, sweep_string=""):
        util.debug(f"Entering expand_sweep_axis: command={command}, target={target},",
                   f"arg_tokens={arg_tokens}, sweep_axis_list={sweep_axis_list}")
        if len(sweep_axis_list) == 0:
            # we aren't sweeping anything, create one job
            snapshot_name = target.replace('../','').replace('/','_') + sweep_string
            eda_path = get_eda_exec('sweep')
            self.jobs.append({
                'name' : snapshot_name,
                'index' : len(self.jobs),
                'command_list' : ([eda_path, command, target, '--job_name', snapshot_name] + arg_tokens)
            })
            return
        sweep_axis = sweep_axis_list[0]
        for v in sweep_axis['values']:
            this_arg_tokens = []
            for a in arg_tokens:
                a_swept = re.sub(rf'\b{sweep_axis["key"]}\b', f"{v}", a)
                this_arg_tokens.append(a_swept)
            next_sweep_axis_list = []
            if len(sweep_axis_list)>1:
                next_sweep_axis_list = sweep_axis_list[1:]
            v_string = f"{v}".replace('.','p')
            self.expand_sweep_axis(command, target, this_arg_tokens, next_sweep_axis_list, sweep_string+f"_{sweep_axis['key']}_{v_string}")

class CommandFList(CommandDesign):
    def __init__(self, config:dict):
        CommandDesign.__init__(self, config, "flist")
        self.args.update({
            'eda-dir'            : 'eda.flist', # use a special directory here if files are generated.
            'out'                : "flist.out",
            'emit-define'        : True,
            'emit-incdir'        : True,
            'emit-v'             : True,
            'emit-sv'            : True,
            'emit-vhd'           : True,
            'emit-cpp'           : True,
            'emit-non-sources'   : True, # as comments, from DEPS 'reqs'
            'prefix-define'      : "+define+",
            'prefix-incdir'      : "+incdir+",
            'prefix-v'           : "",
            'prefix-sv'          : "",
            'prefix-vhd'         : "",
            'prefix-cpp'         : "",
            'prefix-non-sources' : "", # as comments anyway.
            'single-quote-define': False,
            'quote-define'       : True,
            'xilinx'             : False, # we don't want --xilinx to error, but it doesn't do anything much
            'build-script'       : "", # we don't want this to error either

            'print-to-stdout': False, # do not save to file, print to stdout.
            'emit-rel-path'  : False, # ex: eda flist --print-to-stdout --emit-rel-path --quiet <target>
        })

    def set_tool_defines(self):
        pass

    def process_tokens(self, tokens, process_all=True):
        CommandDesign.process_tokens(self, tokens, process_all)
        self.do_it()

    def get_flist_dict(self) -> dict:
        self.set_tool_defines()

        # This will ignore args, and build a dict that an external caller can use, without generating
        # an actual .f file.
        ret = dict()
        for key in ['files_sv', 'files_v', 'files_vhd', 'defines', 'incdirs']:
            # These keys must exist, all are lists, defines is a dict
            x = getattr(self, key, None)
            if type(x) is list or type(x) is dict:
                ret[key] = x.copy()
            else:
                ret[key] = x
        return ret

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        if self.args['top']:
            # check if we're overwriting the output flist file.
            if self.args['print-to-stdout']:
                pass
            elif os.path.exists(self.args['out']):
                if self.args['force']:
                    util.info(f"Removing existing {self.args['out']}")
                    os.remove(self.args['out'])
                else:
                    self.error(f"Not overwriting {self.args['out']} unless you specify --force")

            # Note - we create a work_dir in case any DEPS commands created files that need to be
            # added to our sources.
            self.create_work_dir()
            self.run_dep_commands()

            if self.args['print-to-stdout']:
                fo = None
                print()
            else:
                util.debug(f"Opening {self.args['out']} for writing")
                fo = open( self.args['out'] , 'w' )
                print(f"## {self.args=}", file=fo)

                if self.args['emit-non-sources']:
                    if self.files_non_source:
                        print('## reqs (non-source files that are dependencies):', file=fo)
                        prefix = util.strip_all_quotes(self.args['prefix-non-sources'])
                        for f in self.files_non_source:
                            if self.args['emit-rel-path']: f = os.path.relpath(f)
                            print('##    ' + prefix + f, file=fo)

            if self.args['emit-define']:
                prefix = util.strip_all_quotes(self.args['prefix-define'])
                for d, value in self.defines.items():
                    if self.defines[d] is None:
                        newline = prefix + d
                    else:
                        if self.args['single-quote-define'] : quote = '\''
                        elif self.args['quote-define'] : quote = '"'
                        else : quote = ''
                        if value is None:
                            newline = prefix + quote + d + quote
                        else:
                            newline = prefix + quote + f"{d}={value}" + quote
                    print(newline, file=fo)
            if self.args['emit-incdir']:
                prefix = util.strip_all_quotes(self.args['prefix-incdir'])
                for i in self.incdirs:
                    if self.args['emit-rel-path']: i = os.path.relpath(i)
                    print(prefix + i, file=fo)
            if self.args['emit-v']:
                prefix = util.strip_all_quotes(self.args['prefix-v'])
                for f in self.files_v:
                    if self.args['emit-rel-path']: f = os.path.relpath(f)
                    print(prefix + f, file=fo)
            if self.args['emit-sv']:
                prefix = util.strip_all_quotes(self.args['prefix-sv'])
                for f in self.files_sv:
                    if self.args['emit-rel-path']: f = os.path.relpath(f)
                    print(prefix + f, file=fo)
            if self.args['emit-vhd']:
                prefix = util.strip_all_quotes(self.args['prefix-vhd'])
                for f in self.files_vhd:
                    if self.args['emit-rel-path']: f = os.path.relpath(f)
                    print(prefix + f, file=fo)
            if self.args['emit-cpp']:
                prefix = util.strip_all_quotes(self.args['prefix-cpp'])
                for f in self.files_cpp:
                    if self.args['emit-rel-path']: f = os.path.relpath(f)
                    print(prefix + f, file=fo)

            if self.args['print-to-stdout']:
                print() # don't need to close fo (None)
            else:
                fo.close()
                util.info(f"Created {self.args['out']}")

        self.write_eda_config_and_args()


class CommandWaves(CommandDesign):
    def __init__(self, config:dict):
        Command.__init__(self, config, "waves")

    def process_tokens(self, tokens, process_all=True):
        wave_file = None
        wave_dirs = []
        while len(tokens):
            # see if it's a flag/option like --debug, --seed <n>, etc
            rc = Command.process_tokens(self, tokens, process_all=False)
            if rc == 0:
                continue
            if os.path.isfile(tokens[0]):
                if (wave_file != None):
                    self.error(f"Was already given wave file {wave_file}, not sure what to do with {tokens[0]}")
                wave_file = os.path.abspath(tokens[0])
                tokens.pop(0)
                continue
            if os.path.isdir(tokens[0]):
                if (wave_file != None):
                    self.error(f"Was already given wave file {wave_file}, not sure what to do with {tokens[0]}")
                wave_dirs.append(tokens[0])
            self.error("Didn't understand command token: '%s' in CommandWaves" % (tokens[0]))
        if not wave_file:
            util.info(f"need to look for wave file")
            # we weren't given a wave file, so we will look for one!
            if (len(wave_dirs) == 0) and os.path.isdir(self.args['eda-dir']):
                wave_dirs.append(self.args['eda-dir'])
            if (len(wave_dirs) == 0):
                wave_dirs.append('.')
            all_files = []
            for d in wave_dirs:
                util.info(f"Looking for wavedumps below: {d}")
                for root, dirs, files in os.walk(d):
                    for f in files:
                        for e in [ '.wdb', '.vcd', '.wlf', '.fst' ]:
                            if f.endswith(e):
                                util.info(f"Found wave file: {os.path.join(root,f)}")
                                all_files.append(os.path.join(root,f))
            if len(all_files) > 1:
                all_files.sort(key=lambda f: os.path.getmtime(f))
                util.info(f"Choosing: {self.args['file']} (newest)")
            if len(all_files):
                wave_file = all_files[-1]
            else:
                self.error(f"Couldn't find any wave files below: {','.join(wave_dirs)}")

        wave_file = os.path.abspath(wave_file)
        util.info(f"decided on opening: {wave_file}")

        # TODO(drew): this feels a little customized per-tool, perhaps there's a better
        # way to abstract this configuration for adding other waveform viewers.
        # For example for each command we also have to check shutil.which, because normal Tool
        # classs should work even w/out PATH, but these don't use Tool classes.
        if wave_file.endswith('.wdb'):
            if 'vivado' in self.config['tools_loaded'] and shutil.which('vivado'):
                tcl_name = wave_file + '.waves.tcl'
                with open( tcl_name,'w') as fo :
                    print( 'current_fileset', file=fo)
                    print( 'open_wave_database %s' % wave_file, file=fo)
                command_list = [ 'vivado', '-source', tcl_name]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without Vivado in PATH")
        elif wave_file.endswith('.wlf'):
            if 'questa' in self.config['tools_loaded'] and shutil.which('vsim'):
                command_list = ['vsim', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without Questa in PATH")
        elif wave_file.endswith('.fst'):
            if 'gtkwave' in self.config['tools_loaded'] and shutil.which('gtkwave'):
                command_list = ['gtkwave', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without GtkWave in PATH")
        elif wave_file.endswith('.vcd'):
            if 'questa' in self.config['tools_loaded'] and shutil.which('vsim'):
                command_list = ['vsim', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            elif 'vivado' in self.config['tools_loaded'] and shutil.which('vivado'):
                # I don't think this works, this is a placeholder, I'm sure Vivado can open a VCD
                # Also this would be a great place to start adding some open source (GTKWAVE) support...
                tcl_name = wave_file + '.waves.tcl'
                with open( tcl_name,'w') as fo :
                    print( 'current_fileset', file=fo)
                    print( 'open_wave_database %s' % wave_file, file=fo)
                command_list = [ 'vivado', '-source', tcl_name]
                self.exec(os.path.dirname(wave_file), command_list)
            if 'gtkwave' in self.config['tools_loaded'] and shutil.which('gktwave'):
                command_list = ['gtkwave', wave_file]
                self.exec(os.path.dirname(wave_file), command_list)
            else:
                self.error(f"Don't know how to open {wave_file} without Vivado,",
                           "Questa, or gtkwave in PATH")


class CommandUpload(CommandDesign):

    CHECK_REQUIRES = [Tool]

    def __init__(self, config:dict):
        Command.__init__(self, config, "upload")

    def process_tokens(self, tokens, process_all=True):
        Command.process_tokens(self, tokens, process_all)
        self.create_work_dir()
        self.run_dep_commands()
        self.do_it()

class CommandOpen(CommandDesign):
    def __init__(self, config:dict):
        Command.__init__(self, config, "open")

    def process_tokens(self, tokens, process_all=True):
        Command.process_tokens(self, tokens, process_all)
        self.do_it()

class ToolVerilator(Tool):
    _TOOL = 'verilator'
    _EXE = 'verilator'
    _URL = 'github.com/verilator/verilator'

    def get_versions(self) -> str:
        self.verilator_base_path = ''
        self.verilator_exe = ''
        self.verilator_coverage_exe = ''
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path or not installed, see {self._URL})')
        else:
            self.verilator_exe = path
            self.verilator_base_path, _ = os.path.split(path)

        # Let's get the verilator_coverage path from the same place as verilator.
        if path:
            self.verilator_coverage_exe = shutil.which(
                os.path.join(self.verilator_base_path, 'verilator_coverage')
            )
        if not self.verilator_coverage_exe:
            util.warning(f'"verilator_coverage" not in path, need from same path as "{self.verilator_exe}"')

        version_ret = subprocess.run([self.verilator_exe, '--version'], capture_output=True)
        stdout = version_ret.stdout.decode('utf-8')
        util.debug(f'{path=} {version_ret=}')
        words = stdout.split() # 'Verilator 5.027 devel rev v5.026-92-g403a197e2
        if len(words) < 1:
            self.error(f'{self.verilator_exe} --version: returned unexpected string {version_ret=}')
        version = words[1]
        ver_list = version.split('.')
        if len(ver_list) != 2:
            self.error(f'{self.verilator_exe} --version: returned unexpected string {version_ret=} {version=}')
        self._VERSION = version
        return self._VERSION

    def set_tool_defines(self):
        # We don't need to define VERILATOR, the verilated exe does that itself.
        pass

class CommandSimVerilator(CommandSim, ToolVerilator):
    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolVerilator.__init__(self, config=self.config)
        self.args.update({
            'gui': False,
            'tcl-file': None,
            'dump-vcd': False,
            'lint-only': False,
            'cc-mode': False,
        })
        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

        self.args_help.update({
            'waves':    'Include waveforms, if possible for Verilator by applying' \
            + ' simulation runtime arg +trace. User will need SV code to interpret the plusarg' \
            + ' and apply $dumpfile("dump.fst").',
            'dump-vcd': 'If using --waves, apply simulation runtime arg +trace=vcd. User' \
            + ' will need SV code to interpret the plusarg and apply $dumpfile("dump.vcd").',
            'lint-only': 'Run verilator with --lint-only, instead of --binary',
            'gui':       'Not supported for Verilator',
            'cc-mode':   'Run verilator with --cc, requires a sim_main.cpp or similar sources',
            'optimize':  'Run verilator with: -CLAGS -O3, if no other CFLAGS args are presented',
        })


    def set_tool_defines(self):
        ToolVerilator.set_tool_defines(self)
        self.defines.update(
            self.tool_config.get('defines', {})
        )

    # We do not override CommandSim.do_it()
    def prepare_compile(self):
        self.set_tool_defines()
        if self.args['xilinx']:
            self.error('Error: --xilinx with Verilator is not yet supported', do_exit=False)

        # If there are C++ files here, then we will run Verilator in --cc mode:
        if self.files_cpp:
            self.args['cc-mode'] = True

        # Each of these should be a list of util.ShellCommandList()
        self.verilate_command_lists = self.get_compile_command_lists()
        self.lint_only_command_lists = self.get_compile_command_lists(lint_only=True)
        self.verilated_exec_command_lists  = self.get_simulate_command_lists()
        self.verilated_post_exec_coverage_command_lists = self.get_post_simulate_command_lists()

        paths = ['obj_dir', 'logs']
        util.safe_mkdirs(base=self.args['work-dir'], new_dirs=paths)

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='compile_only.sh',
                                      command_lists=self.verilate_command_lists, line_breaks=True)

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='lint_only.sh',
                                      command_lists=self.lint_only_command_lists, line_breaks=True)

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='simulate_only.sh',
                                      command_lists = self.verilated_exec_command_lists +
                                      (self.verilated_post_exec_coverage_command_lists
                                       if self.args.get('coverage', True) else [])
                                      )

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='all.sh',
                                      command_lists = [
                                          ['./pre_compile_dep_shell_commands.sh'],
                                          ['./compile_only.sh'],
                                          ['./simulate_only.sh'],
                                      ])


    def compile(self):
        if self.args['stop-before-compile']:
            return
        if self.args.get('lint-only', False):
            # We do not scrape compile logs for "must" strings (use_must_strings=False)
            self.run_commands_check_logs(self.lint_only_command_lists, use_must_strings=False)
        else:
            self.run_commands_check_logs(self.verilate_command_lists, use_must_strings=False)

    def elaborate(self):
        pass

    def simulate(self):
        if self.args.get('lint-only', False):
            return

        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            # don't run this if we're stopping before/after compile/elab
            return

        # Note that this is not returning a pass/fail bash return code,
        # so we will likely have to log-scrape to deterimine pass/fail.
        # Also, if we ran in cc-mode, we will not get the "R e p o r t: Verilator" in the sim.exe results,
        # unless that was added to the C++ main.
        use_must_strings = not self.args['cc-mode'] # disable in --cc mode.
        self.run_commands_check_logs(self.verilated_exec_command_lists, use_must_strings=use_must_strings)

        if self.args.get('coverage', True):
            # do not check logs on verilator_coverage commands:
            self.run_commands_check_logs(self.verilated_post_exec_coverage_command_lists, check_logs=False)

    def get_compile_command_lists(self, **kwargs):

        # Support for lint_only (bool) in kwargs:
        lint_only = kwargs.get('lint_only', False)

        verilate_command_list = [
            self.verilator_exe,
        ]
        if self.args['cc-mode']:
            verilate_command_list += [
                '--cc',
                '--build',
                '--exe',
            ]
        elif lint_only:
            verilate_command_list.append('--lint-only')
        else:
            verilate_command_list.append('--binary')


        # Add compile args from our self.config (tools.verilator.compile-args str)
        config_compile_args = self.tool_config.get(
            'compile-args',
            '--timing --assert --autoflush -sv').split()
        verilate_command_list += config_compile_args

        # Add compile waivers from self.config (tools.verilator.compile-waivers list):
        # list(set(mylist)) to get unique.
        for waiver in self.tool_config.get(
                'compile-waivers',
                [ #defaults:
                    'CASEINCOMPLETE',
                    'TIMESCALEMOD', # If one file has `timescale, then they all must
                ]):
            verilate_command_list.append(f'-Wno-{waiver}')

        # measurements taken from running eda multi sim top/tests/oc.*test --parallel 8 on AMD 5950X
        #  oc_chip_status_test  vvv               fast compile, very long runtime (simulation dominated)
        #  oc_cos_mbist_4x32_test     vvv         long compile, not long runtime  (compile/elab dominated)
        #'-CFLAGS', '-O0', # 7:43 - 9:09
        #'-CFLAGS', '-O1', # 0:30 - 3:47
        #'-CFLAGS', '-O2', # 0:24 - 5:55
        #'-CFLAGS', '-O3', # 0:22 - 6:07

        # We can only support one -CFLAGS followed by one -O[0-9] arg in self.args['verilate-args']:
        # TODO(drew): move this to util, sanitize verilate and compiler args:
        verilate_cflags_args_dict = dict()
        verilate_args = list() # will be combined verilate_args + compile-args
        prev_arg_is_cflags = False
        util.debug(f"{self.args['verilate-args']=}")
        util.debug(f"{self.args['compile-args']=}")
        for iter, arg in enumerate(self.args['verilate-args'] + self.args['compile-args']):
            # pick the first ones we see of these:
            if arg == '-CFLAGS':
                prev_arg_is_cflags = True
                if arg not in verilate_cflags_args_dict:
                    # We can only have 1
                    verilate_cflags_args_dict[arg] = True
                    verilate_args.append(arg)
                else:
                    util.debug('fPrevious saw -CFLAGS args {verilate_cflags_args_dict=}, skipping new {arg=}')

            elif arg.startswith('-O') and len(arg) == 3:
                if '-O' not in verilate_cflags_args_dict and prev_arg_is_cflags:
                    # We can only have 1
                    verilate_cflags_args_dict['-O'] = arg[-1]
                    verilate_args.append(arg)
                else:
                    util.debug('fPrevious saw -CFLAGS args {verilate_cflags_args_dict=}, skipping new {arg=}')
                prev_arg_is_cflags = False

            else:
                prev_arg_is_cflags = False
                verilate_args.append(arg)

        util.debug(f'{verilate_args=}')

        if '-CFLAGS' in verilate_args:
            # add whatever args were passed via 'compile-args' or 'verilate_args'. Note these will
            # take precedence over the --optimize arg.
            pass
        elif self.args['optimize']:
            verilate_command_list += '-CFLAGS', '-O3' # if a test is marked --optimize then we give it --O3 to pull down runtime
        else:
            verilate_command_list += '-CFLAGS', '-O1' # else we use -O1 which has best overall behavior

        verilate_command_list += verilate_args

        if self.args.get('waves', False) and not lint_only:
            # Skip waves if this is elab or lint_only=True
            config_waves_args = self.tool_config.get(
                'compile-waves-args',
                '--trace-structs --trace-params').split()
            verilate_command_list += config_waves_args
            if self.args.get('dump-vcd', False):
                verilate_command_list += [ '--trace' ]
            else:
                verilate_command_list += [ '--trace-fst' ]


        if self.args.get('coverage', True):
            verilate_command_list += self.tool_config.get(
                'compile-coverage-args', '--coverage').split()

        verilate_command_list += [
            '-top', self.args['top'],
        ]

        if not lint_only:
            verilate_command_list += [
                '-o', 'sim.exe',
            ]

        # incdirs
        for value in self.incdirs:
            verilate_command_list += [ f"+incdir+{value}" ]

        # defines
        for k,v in self.defines.items():
            if v is None:
                verilate_command_list += [ f'+define+{k}' ]
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}, but also for SystemVerilog plusargs
                verilate_command_list += [ f'+define+{k}={sanitize_defines_for_sh(v)}' ]

        if (len(self.files_sv) + len(self.files_v)) == 0:
            self.error(f'{self.target=} {self.files_sv=} and {self.files_v=} are empty, cannot call verilator')

        verilate_command_list += list(self.files_sv) + list(self.files_v)

        if self.args['cc-mode']:
            # Verilator --cc mode, we have to also add the C++ file to our verilate command:
            verilate_command_list += list(self.files_cpp)

        return [ util.ShellCommandList(verilate_command_list, tee_fpath='compile.log') ]


    def get_simulate_command_lists(self):

        # verilator needs the seed to be < 2*31-1
        verilator_seed = int(self.args['seed']) & 0xfff_ffff

        assert type(self.args['sim-plusargs']) is list, \
            f'{self.target=} {type(self.args["sim-plusargs"])=} but must be list'

        sim_plusargs = list()
        for x in self.args['sim-plusargs']:
            # For Verilator we need to add a +key=value if the + is missing
            if x[0] != '+':
                x = f'+{x}'
            sim_plusargs.append(x)

        # TODO(drew): don't have a use-case yet for self.args['sim-library', 'elab-args'] in the verilated executable
        # 'simulation' command list, but we may need to support them if we have more than 'work' library.


        verilated_exec_command_list = [
            './obj_dir/sim.exe',
        ]

        config_sim_args = self.tool_config.get(
            'simulate-args',
            f'+verilator+error+limit+100').split()

        if self.args['waves']:
            sim_waves_args_list = self.tool_config.get('simulate-waves-args', '').split()
            config_sim_args += sim_waves_args_list
            if not any([x.startswith('+trace=') or x == '+trace' for x in \
                        config_sim_args + sim_plusargs + self.args['sim-args']]):
                # Built-in support for eda args --waves and/or --dump-vcd to become runtime
                # plusargs +trace or +trace=vcd, if +trace or +trace= was not already in our plusargs.
                if self.args.get('dump-vcd', False):
                    sim_plusargs.append('+trace=vcd')
                else:
                    sim_plusargs.append('+trace')

        verilated_exec_command_list += config_sim_args + sim_plusargs + self.args['sim-args']


        # We need to set the seed if none of the other args did:
        if not any([x.startswith('+verilator+seed+') for x in verilated_exec_command_list]):
            verilated_exec_command_list.append(f'+verilator+seed+{verilator_seed}')

        return [ util.ShellCommandList(verilated_exec_command_list, tee_fpath='sim.log') ] # single entry list


    def get_post_simulate_command_lists(self):

        if self.args.get('coverage', True):
            if not self.verilator_coverage_exe:
                self.error(f'verilator_coverage not found in path with {self.verilator_exe}')
                return []

            verilated_post_exec_coverage_command_list = [self.verilator_coverage_exe]
            config_coverage_args = self.tool_config.get(
                'coverage-args',
                '--annotate logs/annotated --annotate-min 1 coverage.dat').split()

            verilated_post_exec_coverage_command_list += config_coverage_args

            return [ util.ShellCommandList(verilated_post_exec_coverage_command_list,
                                           tee_fpath='coverage.log') ] # single entry list
        else:
            return []



class CommandElabVerilator(CommandSimVerilator):
    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True
        self.args['lint-only'] = True


class ToolYosys(Tool):
    '''Parent class for ToolTabbyCadYosys, ToolInvioYosys, ToolSlangYosys'''
    _TOOL = 'yosys'
    _EXE = 'yosys'
    _URL = 'https://yosyshq.readthedocs.io/en/latest/'

    def get_versions(self) -> str:
        self.yosys_exe = ''
        if self._VERSION:
            return self._VERSION

        path = shutil.which(self._EXE)
        if not path:
            self.error('"{self._EXE}" not in path or not installed, see {self._URL}')
        else:
            self.yosys_exe = path

        # Unforunately we don't have a non-PATH friendly support on self._EXE to set
        # where standalone 'sta' is. Even though Yosys has 'sta' internally, Yosys does
        # not fully support timing constraints or .sdc files, so we have to run 'sta'
        # standalone.
        self.sta_exe = ''
        self.sta_version = ''
        sta_path = shutil.which('sta')
        if sta_path:
            util.debug(f'Also located "sta" via {sta_path}')
            self.sta_exe = sta_path
            sta_version_ret = subprocess.run( [self.sta_exe, '-version'], capture_output=True )
            util.debug(f'{self.yosys_exe} {sta_version_ret=}')
            sta_ver = sta_version_ret.stdout.decode('utf-8').split()[0]
            if sta_ver:
                self.sta_version = sta_ver

        version_ret = subprocess.run( [self.yosys_exe, '--version'], capture_output=True )
        util.debug(f'{self.yosys_exe} {version_ret=}')
        words = version_ret.stdout.decode('utf-8').split() # Yosys 0.48 (git sha1 aaa534749, clang++ 14.0.0-1ubuntu1.1 -fPIC -O3)
        if len(words) < 2:
            self.error(f'{self.yosys_exe} --version: returned unexpected str {version_ret=}')
        self._VERSION = words[1]
        return self._VERSION

    def set_tool_defines(self):
        self.defines.update({
            'OC_TOOL_YOSYS': None
        })
        if self.args['xilinx']:
            self.defines.update({
                'OC_LIBRARY_ULTRASCALE_PLUS': None,
                'OC_LIBRARY': "1"
            })
        else:
            self.defines.update({
                'OC_LIBRARY_BEHAVIORAL': None,
                'OC_LIBRARY': "0"
            })


class ToolTabbyCadYosys(ToolYosys):
    _TOOL = 'tabbycad_yosys'
    _URL = 'https://www.yosyshq.com/tabby-cad-datasheet'

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_TABBYCAD': None,
        })


class CommandSynthTabbyCadYosys(CommandSynth, ToolTabbyCadYosys):
    def __init__(self, config:dict):
        CommandSynth.__init__(self, config)
        ToolTabbyCadYosys.__init__(self, config=self.config)
        self.args.update({
            'yosys-synth': 'synth',              # synth_xilinx, synth_altera, etc (see: yosys help)
            'yosys-pre-synth': ['prep', 'proc'], # command run in yosys prior to yosys-synth command.
            'yosys-blackbox': [],                # list of modules that yosys will blackbox.
        })


    def do_it(self):
        self.set_tool_defines()
        self.write_eda_config_and_args()

        if self.is_export_enabled():
            self.do_export()
            return self.status

        self._write_and_run_yosys_f_files()

    def _write_and_run_yosys_f_files(self):
        '''
        1. Creates and runs: yosys.verific.f
           -- should create post_verific_ls.txt
        2. python will examine this .txt file and compare to our blackbox_list (modules)
        3. Creates and runs: yosys.synth.f
           -- does blackboxing and synth steps
        4. Creates a wrapper for human debug and reuse: yosys.f
        '''

        script_synth_lines = list()
        script_f = [
            'script yosys.verific.f',
            'script yosys.synth.f',
        ]

        # Note - big assumption here that "module myname" is contained in myname.[v|sv]:
        # Note - we use both synth-blackbox and yosys-blackbox lists to blackbox modules in yosys (not verific)
        blackbox_list = self.args.get('yosys-blackbox', list()) + self.args.get('synth-blackbox', list())
        blackbox_files_list = list()
        for path in self.files_v + self.files_sv:
            leaf_filename = path.split('/')[-1]
            module_name = ''.join(leaf_filename.split('.')[:-1])
            if module_name in blackbox_list:
                blackbox_files_list.append(path)
        util.debug(f'tabbycad_yosys: {blackbox_list=}')

        # create {work_dir} / yosys
        work_dir = self.args.get('work-dir', '')
        assert work_dir
        work_dir = os.path.abspath(work_dir)
        verific_out_dir = os.path.join(work_dir, 'verific')
        yosys_out_dir = os.path.join(work_dir, 'yosys')
        for p in [verific_out_dir, yosys_out_dir]:
            util.safe_mkdir(p)

        verific_v_path = os.path.join(verific_out_dir, f'{self.args["top"]}.v')
        yosys_v_path = os.path.join(yosys_out_dir, f'{self.args["top"]}.v')


        script_verific_lines = list()
        for name,value in self.defines.items():
            if not name:
                continue
            if name in ['SIMULATION']:
                continue

            if value is None:
                script_verific_lines.append(f'verific -vlog-define {name}')
            else:
                script_verific_lines.append(f'verific -vlog-define {name}={value}')

        # We must define SYNTHESIS for oclib_defines.vh to work correctly.
        if 'SYNTHESIS' not in self.defines:
            script_verific_lines.append('verific -vlog-define SYNTHESIS')

        for path in self.incdirs:
            script_verific_lines.append(f'verific -vlog-incdir {path}')

        for path in self.files_v:
            script_verific_lines.append(f'verific -sv {path}')

        for path in self.files_sv:
            script_verific_lines.append(f'verific -sv {path}')

        for path in self.files_vhd:
            script_verific_lines.append(f'verific -vhdl {path}')

        script_verific_lines += [
            # This line does the 'elaborate' step, and saves out a .v to verific_v_path.
            f'verific -import -vv -pp {verific_v_path} {self.args["top"]}',
            # this ls command will dump all the module instances, which we'll need to
            # know for blackboxing later.
            'tee -o post_verific_ls.txt ls',
        ]

        yosys_verific_f_path = os.path.join(work_dir, 'yosys.verific.f')
        with open(yosys_verific_f_path, 'w') as f:
            f.write('\n'.join(script_verific_lines))

        # Run our created yosys.verific.f script
        # Note - this will always run, even if --stop-before-compile is set.
        self.exec(work_dir=work_dir, command_list=['yosys', '--scriptfile', yosys_verific_f_path],
                  tee_fpath='yosys.verific.log')
        util.info('yosys.verific.f: wrote: ' + os.path.join(work_dir, 'post_verific_ls.txt'))

        # Based on the results in post_verific_ls.txt, create blackbox commands for yosys.synth.f script.
        yosys_blackbox_list = list()
        with open(os.path.join(work_dir, 'post_verific_ls.txt')) as f:
            # compare these against our blackbox modules:
            for line in f.readlines():
                util.debug(f'post_verific_ls.txt: {line=}')
                if line.startswith('  '):
                    line = line.strip()
                    if len(line.split()) == 1:
                        # line has 1 word and starts with leading spaces:
                        # get the base module if it has parameters, etc:
                        # verific in TabbyCAD will output something like foo(various_parameters...), so the base
                        # module is before the '(' in their instance name.
                        base_module = line.split('(')[0]
                        if base_module in blackbox_list:
                            yosys_blackbox_list.append(line) # we need the full (stripped whitespace) line


        # Create yosys.synth.f
        yosys_synth_f_path = os.path.join(work_dir, 'yosys.synth.f')
        synth_command = self.args.get('yosys-synth', 'synth')

        with open(yosys_synth_f_path, 'w') as f:
            lines = [
                # Since we exited yosys, we have to re-open the verific .v file
                f'verific -sv {verific_v_path}',
                # We also have to re-import it (elaborate) it.
                f'verific -import {self.args["top"]}',
            ]

            for inst in yosys_blackbox_list:
                lines.append('blackbox ' + inst)

            lines += self.args.get('yosys-pre-synth', [])
            lines += [
                synth_command,
                f'write_verilog {yosys_v_path}'
            ]
            f.write('\n'.join(lines))

        # We create a yosys.f wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_yosys.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                util.ShellCommandList(['yosys', '--scriptfile', 'yosys.verific.f'], tee_fpath='yosys.verific.log'),
                util.ShellCommandList(['yosys', '--scriptfile', 'yosys.synth.f'], tee_fpath='yosys.synth.log'),
            ],
        )

        # Do not run this if args['stop-before-compile'] is True
        # TODO(drew): I could move this earlier if I ran this whole process out of
        # a side generated .py file.
        if self.args.get('stop-before-compile', False):
            return

        # Run these commands.
        self.exec(work_dir=work_dir, command_list=['yosys', '--scriptfile', yosys_synth_f_path],
                  tee_fpath='yosys.synth.log')
        if self.status == 0:
            util.info(f'yosys: wrote verilog to {yosys_v_path}')
        return self.status


class ToolInvioYosys(ToolYosys):
    _TOOL = 'invio_yosys'
    _URL = 'https://www.verific.com/products/invio/'
    _EXE = 'yosys'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        # We also have to make sure invio-py exists, or that we can import invio within python.
        invio_py_path = shutil.which('invio-py')
        if not invio_py_path:
            try:
                import invio
            except:
                self.error('"invio-py" not in path, or invio package not in python env')

        yosys_path = shutil.which(self._EXE)
        if not yosys_path:
            self.error('"{self._EXE}" not in path')
        else:
            self.yosys_exe = yosys_path

        return super().get_versions()

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_INVIO': None,
        })


class CommandSynthInvioYosys(CommandSynth, ToolInvioYosys):
    def __init__(self, config:dict):
        CommandSynth.__init__(self, config)
        ToolInvioYosys.__init__(self, config=self.config)
        self.args.update({
            'invio-blackbox': [],                # list of modules that invio/verific will blackbox.
            'yosys-synth': 'synth_xilinx',       # synth_xilinx, synth_altera, etc (see: yosys help)
            'yosys-pre-synth': ['prep', 'proc'], # command run in yosys prior to yosys-synth command.
            'yosys-blackbox': [],                # list of modules that yosys will blackbox.
        })


    def do_it(self):
        self.set_tool_defines()
        self.write_eda_config_and_args()

        if self.is_export_enabled():
            self.do_export()
            return self.status

        self._invio_write_verilog()

    def _invio_write_verilog(self):

        # Use helper module for Invio/Verific to save out Verilog-2001 from our
        # Verilog + SystemVerilog + VHDL file lists.
        from opencos import invio_helpers
        invio_blackbox_list = self.args.get('invio-blackbox', list())

        # Generate run_invio.py:
        invio_dict = invio_helpers.get_invio_command_dict(
            self, blackbox_list=invio_blackbox_list, sim_elab=False
        )
        # run run_invio.py:
        if not self.args.get('stop-before-compile', False):
            for cmdlist in invio_dict['command_lists']:
                self.exec( self.args['work-dir'], cmdlist, tee_fpath=cmdlist.tee_fpath )
            util.info(f'invio/verific: wrote verilog to {invio_dict.get("full_v_filename", None)}')

        # create {work_dir} / yosys
        work_dir = invio_dict.get('work_dir', '')
        assert work_dir
        fullp = os.path.join(work_dir, "yosys")
        if not os.path.exists(fullp):
            os.mkdir(fullp)

        # create yosys.f so we can run a few commands within yosys.
        yosys_f_path = os.path.join(work_dir, 'yosys.f')
        yosys_v_path = os.path.join(work_dir, 'yosys', invio_dict['v_filename'])

        synth_command = self.args.get('yosys-synth', 'synth')

        with open(yosys_f_path, 'w') as f:
            lines = list()
            for path in invio_dict.get('blackbox_files_list', list()):
                # We have to read the verilog files from the invio blackbox_files_list:
                lines.append(f'read_verilog {path}')
            for module in self.args.get('yosys-blackbox', list()) + self.args.get('synth-blackbox', list()):
                # But we may blackbox different cells for yosys synthesis.
                lines.append(f'blackbox {module}')

            lines.append(f'read_verilog {invio_dict["full_v_filename"]}')
            lines += self.args.get('yosys-pre-synth', [])
            lines += [
                synth_command,
                f'write_verilog {yosys_v_path}'
            ]
            f.write('\n'.join(lines))

        synth_command_list = util.ShellCommandList(
            [self.yosys_exe, '--scriptfile', yosys_f_path], tee_fpath='yosys.synth.log'
        )


        invio_command_list = util.ShellCommandList(
            ['python3', invio_dict['full_py_filename']], tee_fpath=invio_dict['full_py_filename']
        )

        # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_invio.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                invio_command_list
            ],
        )
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_invio_yosys.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                invio_command_list,
                synth_command_list,
            ],
        )

        # Do not run this if args['stop-before-compile'] is True
        if self.args.get('stop-before-compile', False) or \
           self.args.get('stop-after-compile', False):
            pass # skip it.
        else:
            self.exec(work_dir=work_dir, command_list=synth_command_list, tee_fpath=synth_command_list.tee_fpath)
            util.info(f'yosys: wrote verilog to {yosys_v_path}')
        return self.status


class CommandElabInvioYosys(CommandSynthInvioYosys):
    '''Run invio + yosys as elab only (does not run the synthesis portion)'''
    def __init__(self, config):
        super().__init__(config)
        self.command_name = 'elab'
        self.args.update({
            'stop-after-compile': True, # For this, we run the Invio step
            'lint': True
        })


class ToolSlangYosys(ToolYosys):
    '''Uses slang.so in yosys plugins directory, called via yosys > plugin -i slang'''
    _TOOL = 'slang_yosys'
    _URL = [
        'https://github.com/povik/yosys-slang',
        'https://github.com/The-OpenROAD-Project/OpenSTA',
        'https://yosyshq.readthedocs.io/en/latest/',
        'https://github.com/MikePopoloski/slang',
    ]

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_SLANG': None,
        })


class CommandSynthSlangYosys(CommandSynth, ToolSlangYosys):
    def __init__(self, config:dict):
        CommandSynth.__init__(self, config)
        ToolSlangYosys.__init__(self, config=self.config)
        self.args.update({
            'sta': False,
            'liberty-file': '',
            'sdc-file': '',
            ### TODO(drew): ??? 'yosys-synth-flatten': True,
            'yosys-synth': 'synth',       # synth_xilinx, synth_altera, etc (see: yosys help)
            'yosys-pre-synth': ['prep', 'proc'], # command run in yosys prior to yosys-synth command.
            'yosys-blackbox': [],                # list of modules that yosys will blackbox.
        })
        self.args_help.update({
            'sta': 'After running Yosys, run "sta" with --liberty-file.' \
            + ' sta can be installed via: https://github.com/The-OpenROAD-Project/OpenSTA',
            'sdc-file': '.sdc file to use with --sta, if not present will use auto constraints',
            'liberty-file': 'Single liberty file for synthesis and sta,' \
            + ' for example: github/OpenSTA/examples/nangate45_slow.lib.gz',
            ###'yosys-synth-flatten': 'Controls if Yosys synth should be run with -flatten flag',
            'yosys-synth': 'The synth command provided to Yosys, see: yosys help.',
            'yosys-pre-synth': 'Yosys commands performed prior to running "synth"' \
            + ' (or eda arg value for --yosys-synth)',
            'yosys-blackbox': 'List of modules that yosys will blackbox, likely will need these' \
            + ' in Verilog-2001 for yosys to read outside of slang and synth',
        })

    def do_it(self):
        self.set_tool_defines()
        self.write_eda_config_and_args()

        if self.is_export_enabled():
            self.do_export()
            return self.status

        self._write_and_run_yosys_f_files()

    def _write_and_run_yosys_f_files(self):
        '''
        1. Creates and runs: yosys.slang.f
           -- should create post_slang_ls.txt
        2. python will examine this .txt file and compare to our blackbox_list (modules)
        3. Creates and runs: yosys.synth.f
           -- does blackboxing and synth steps
        4. Creates a wrapper for human debug and reuse: yosys.f
        '''

        script_synth_lines = list()
        script_f = [
            'script yosys.slang.f',
            'script yosys.synth.f',
        ]

        # Note - big assumption here that "module myname" is contained in myname.[v|sv]:
        # Note - we use both synth-blackbox and yosys-blackbox lists to blackbox modules in yosys (not slang)
        blackbox_list = self.args.get('yosys-blackbox', list()) + self.args.get('synth-blackbox', list())
        blackbox_files_list = list()
        for path in self.files_v + self.files_sv:
            leaf_filename = path.split('/')[-1]
            module_name = ''.join(leaf_filename.split('.')[:-1])
            if module_name in blackbox_list:
                blackbox_files_list.append(path)
        util.debug(f'slang_yosys: {blackbox_list=}')

        # create {work_dir} / yosys
        work_dir = self.args.get('work-dir', '')
        assert work_dir
        work_dir = os.path.abspath(work_dir)
        slang_out_dir = os.path.join(work_dir, 'slang')
        yosys_out_dir = os.path.join(work_dir, 'yosys')
        for p in [slang_out_dir, yosys_out_dir]:
            util.safe_mkdir(p)

        slang_v_path = os.path.join(slang_out_dir, f'{self.args["top"]}.v')
        yosys_v_path = os.path.join(yosys_out_dir, f'{self.args["top"]}.v')


        script_slang_lines = [
            'plugin -i slang'
        ]

        read_slang_cmd = [
            'read_slang',
            '--ignore-unknown-modules',
            '--best-effort-hierarchy',
        ]

        for name,value in self.defines.items():
            if not name:
                continue
            if name in ['SIMULATION']:
                continue

            if value is None:
                read_slang_cmd.append(f'--define-macro {name}')
            else:
                read_slang_cmd.append(f'--define-macro {name}={value}')

        # We must define SYNTHESIS for oclib_defines.vh to work correctly.
        if 'SYNTHESIS' not in self.defines:
            read_slang_cmd.append('--define-macro SYNTHESIS')

        for path in self.incdirs:
            read_slang_cmd.append(f'-I {path}')

        for path in self.files_v:
            read_slang_cmd.append(path)

        for path in self.files_sv:
            read_slang_cmd.append(path)

        read_slang_cmd.append(f'--top {self.args["top"]}')

        script_slang_lines += [
            ' '.join(read_slang_cmd), # one liner.
            # This line does the 'elaborate' step, and saves out a .v to slang_v_path.
            f'write_verilog {slang_v_path}',
            # this ls command will dump all the module instances, which we'll need to
            # know for blackboxing later. This is not in bash, this is within slang
            'tee -o post_slang_ls.txt ls',
        ]

        yosys_slang_f_path = os.path.join(work_dir, 'yosys.slang.f')
        with open(yosys_slang_f_path, 'w') as f:
            f.write('\n'.join(script_slang_lines))

        # Run our created yosys.slang.f script
        # Note - this will always run, even if --stop-before-compile is set.
        slang_command_list = util.ShellCommandList([self.yosys_exe, '--scriptfile', 'yosys.slang.f'],
                                                   tee_fpath = 'yosys.slang.log')
        self.exec(work_dir=work_dir, command_list=slang_command_list,
                  tee_fpath=slang_command_list.tee_fpath)
        util.info('yosys.slang.f: wrote: ' + os.path.join(work_dir, 'post_slang_ls.txt'))

        # Based on the results in post_slang_ls.txt, create blackbox commands for yosys.synth.f script.
        yosys_blackbox_list = list()
        with open(os.path.join(work_dir, 'post_slang_ls.txt')) as f:
            # compare these against our blackbox modules:
            for line in f.readlines():
                util.debug(f'post_slang_ls.txt: {line=}')
                if line.startswith('  '):
                    line = line.strip()
                    if len(line.split()) == 1:
                        # line has 1 word and starts with leading spaces:
                        # get the base module if it has parameters, etc:
                        # slang will output something like foo$various_parameters, so the base
                        # module is before the $ in their instance name.
                        base_module = line.split('$')[0]
                        if base_module in blackbox_list:
                            yosys_blackbox_list.append(line) # we need the full (stripped whitespace) line


        # Create yosys.synth.f
        yosys_synth_f_path = os.path.join(work_dir, 'yosys.synth.f')
        synth_command = self.args.get('yosys-synth', 'synth')
        if self.args['flatten-all']:
            synth_command += ' -flatten'

        if self.args['liberty-file'] and not os.path.exists(self.args['liberty-file']):
            self.error(f'--liberty-file={self.args["liberty-file"]} file does not exist')

        with open(yosys_synth_f_path, 'w') as f:
            lines = [
                # Since we exited yosys, we have to re-open the slang .v file
                f'read_verilog -sv -icells {slang_v_path}',
            ]

            if self.args['liberty-file']:
                lines.append('read_liberty -lib ' + self.args['liberty-file'])

            for inst in yosys_blackbox_list:
                lines.append('blackbox ' + inst)

            lines += self.args.get('yosys-pre-synth', [])
            lines.append(synth_command)

            # TODO(drew): I need a blackbox flow here? Or a memory_libmap?
            #   --> https://yosyshq.readthedocs.io/projects/yosys/en/latest/cmd/memory_libmap.html
            # TODO(drew): can I run multiple liberty files?
            if self.args['liberty-file']:
                lines += [
                    'dfflibmap -liberty ' + self.args['liberty-file'],
                    #'memory_libmap -lib ' + self.args['liberty-file'], # Has to be unzipped?
                    'abc -liberty  ' + self.args['liberty-file'],
                ]

            lines.append(f'write_verilog {yosys_v_path}')
            f.write('\n'.join(lines))

        synth_command_list = util.ShellCommandList(
            [self.yosys_exe, '--scriptfile', 'yosys.synth.f'],
            tee_fpath = 'yosys.synth.log'
        )

        sta_command_list = []
        if self.args['sta']:
            if not self.args['liberty-file']:
                self.error(f'--sta is set, but need to also set --liberty-file=<file>')

            if self.args['sdc-file']:
                if not os.path.exists(self.args['sdc-file']):
                    self.error(f'--sdc-file={self.args["sdc-file"]} file does not exist')

            if not self.sta_exe:
                self.error(f'--sta is set, but "sta" was not found in PATH, see: {self._URL}')

            sta_command_list = util.ShellCommandList(
                [ self.sta_exe, '-no_init', '-exit', 'sta.f' ],
                tee_fpath = 'sta.log'
            )

            # Need to create sta.f:
            if self.args['sdc-file']:
                sdc_path = self.args['sdc-file']
            else:
                sdc_path = 'sdc.f'

            with open(os.path.join(self.args['work-dir'], 'sta.f'), 'w') as f:
                lines = [
                    'read_liberty ' + self.args['liberty-file'],
                    'read_verilog ' + yosys_v_path,
                    'link_design ' + self.args['top'],
                    'read_sdc ' + sdc_path,
                    'report_checks',
                ]
                f.write('\n'.join(lines))

            # Need to create sta.sdc, or use the user provided one.
            if not self.args['sdc-file']:
                with open(os.path.join(self.args['work-dir'], 'sdc.f'), 'w') as f:
                    clock_name = self.args['clock-name']
                    period = self.args['clock-ns']
                    name_not_equal_clocks_str = f'NAME !~ "{clock_name}"'
                    lines = [
                        f'create_clock -add -name {clock_name} -period {period} [get_ports ' \
                        + '{' + clock_name + '}];',
                        f'set_input_delay -max {self.args["idelay-ns"]} -clock {clock_name}' \
                        + ' [get_ports * -filter {DIRECTION == IN && ' + name_not_equal_clocks_str + '}];',
                        f'set_output_delay -max {self.args["odelay-ns"]} -clock {clock_name}' \
                        + ' [get_ports * -filter {DIRECTION == OUT}];',
                    ]
                    f.write('\n'.join(lines))

            sta_command_list = util.ShellCommandList(
                sta_command_list,
                tee_fpath = 'sta.log'
            )


        # We create a run_yosys.sh wrapping these scripts, but we do not run this one.
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_yosys.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                slang_command_list,
                synth_command_list,
                sta_command_list,
            ],
        )
        util.write_shell_command_file(
            dirpath=self.args['work-dir'],
            filename='run_slang.sh',
            command_lists=[
                # Gives us bash commands with tee and pipstatus:
                slang_command_list,
            ],
        )

        # Do not run this if args['stop-before-compile'] is True
        # TODO(drew): I could move this earlier if I ran this whole process out of
        # a side generated .py file, but we need to query things to generate the synth script.
        if self.args.get('stop-before-compile', False):
            return

        # Run the synth commands standalone:
        self.exec(work_dir=work_dir, command_list=synth_command_list,
                  tee_fpath=synth_command_list.tee_fpath)

        if self.args['sta']:
            self.exec(work_dir=work_dir, command_list=sta_command_list,
                      tee_fpath=sta_command_list.tee_fpath)

        if self.status == 0:
            util.info(f'yosys: wrote verilog to {yosys_v_path}')
        return self.status


class CommandElabSlangYosys(CommandSynthSlangYosys):
    '''Run slang-yosys as elab only (does not run the synthesis portion)'''
    def __init__(self, config):
        super().__init__(config)
        self.command_name = 'elab'
        self.args.update({
            'stop-before-compile': True,
            'lint': True
        })

class ToolInvio(Tool):
    '''Invio w/out Yosys, used for elab in SIMULATIION (not the same as ToolInvioYosys)'''
    _TOOL = 'invio'
    _URL = 'https://www.verific.com/products/invio/'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION

        # We also have to make sure invio-py exists, or that we can import invio within python.
        invio_py_path = shutil.which('invio-py')
        if not invio_py_path:
            try:
                import invio
            except:
                self.error('"invio-py" not in path, or invio package not in python env')

        return super().get_versions()

    def set_tool_defines(self):
        super().set_tool_defines()
        self.defines.update({
            'OC_TOOL_INVIO': None,
        })


class CommandElabInvio(CommandElab, ToolInvio):
    def __init__(self, config:dict):
        CommandElab.__init__(self, config)
        ToolInvio.__init__(self, config=self.config)
        self.args.update({
            'invio-blackbox': [],                # list of modules that invio/verific will blackbox.
        })

        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

        self.invio_command_lists = []

    # Note that we follow parent class CommandSim's do_it() flow, that way --export args
    # are handled.
    def prepare_compile(self):
        ''' prepare_compile() - following parent Commandsim's run() flow'''
        self.set_tool_defines()
        self.write_eda_config_and_args()

        self.invio_command_lists = self.get_compile_command_lists()
        self.write_invio_sh()

    def compile(self):
        pass

    def elaborate(self):
        ''' elaborate() - following parent Commandsim's run() flow, runs invio_command_lists'''
        if self.args['stop-before-compile'] or \
           self.args['stop-after-compile']:
            return
        # Finally, run the command(s) if we made it this far: python run_invio.py:
        self.run_commands_check_logs(self.invio_command_lists)

    def get_compile_command_lists(self) -> list:
        '''Returns list of util.ShellCommandList, for slang we'll run this in elaborate()'''
        from opencos import invio_helpers
        invio_blackbox_list = self.args.get('invio-blackbox', list())
        invio_dict = invio_helpers.get_invio_command_dict(
            self, blackbox_list=invio_blackbox_list, sim_elab=True
        )
        return invio_dict['command_lists']

    def write_invio_sh(self):
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_invio.sh',
                                      command_lists=self.invio_command_lists, line_breaks=True)



class ToolSlang(Tool):
    _TOOL = 'slang'
    _EXE = 'slang'
    _URL = 'https://github.com/MikePopoloski/slang'

    def get_versions(self) -> str:
        self.slang_exe = ''
        self.slang_base_path = ''
        self.slang_tidy_exe = ''
        self.slang_hier_exe = ''
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path, need to get it ({self._URL}')
        else:
            self.slang_exe = path
            self.slang_base_path, _ = os.path.split(path)
            self.slang_tidy_exe = os.path.join(self.slang_base_path, 'slang-tidy')
            self.slang_hier_exe = os.path.join(self.slang_base_path, 'slang-hier')

        version_ret = subprocess.run( [self.slang_exe, '--version'], capture_output=True )
        stdout = version_ret.stdout.decode('utf-8')
        util.debug(f'{path=} {version_ret=}')
        words = stdout.split() # slang version 8.0.6+b4a74b00
        if len(words) < 3:
            self.error(f'{self.slang_exe} --version: returned unexpected string {version_ret=}')
        version = words[2]
        left, right = version.split('+')
        ver_list = left.split('.')
        if len(ver_list) != 3:
            self.error(f'{self.slang_exe} --version: returned unexpected string {version_ret=} {version=}')
        self._VERSION = left
        return self._VERSION

    def set_tool_defines(self):
        self.defines['OC_TOOL_SLANG'] = None # add define
        if 'SYNTHESIS' not in self.defines:
            self.defines['SIMULATION'] = None # add define
        # Expected to manually add SYNTHESIS command line or target, otherwise.
        # Similarly, you could use --tool slang_yosys for a synthesis friendly
        # elab in Yosys.


class CommandElabSlang(CommandElab, ToolSlang):
    def __init__(self, config:dict):
        CommandElab.__init__(self, config)
        ToolSlang.__init__(self, config=self.config)
        self.args.update({
            'slang-args': list(), # aka, --single-unit, --ast-json <fname>, --ast-json-source-info
            'slang-json': False, # sets all the args I know of for AST.
            'slang-top': '',
            'tidy': False, # run slang-tidy instead of slang
            'hier': False, # run slang-hier instead of slang
        })

        self.all_json_args = [
            '--ast-json', ## needs filename: slang.json'
            '--ast-json-source-info',
            '--ast-json-detailed-types',
        ]

        self.args_help.update({
            'tidy': "Runs 'slang-tidy' instead of 'slang', with no ast- args.",
            'hier': "Runs 'slang-hier' instead of 'slang', with no ast- args.",
        })

        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

        # If we're in elab, so not in general ToolSlang, set define for SLANG
        self.defines.update({
            'SLANG': 1
        })

        self.slang_command_lists = []


    # Note that we follow parent class CommandSim's do_it() flow, that way --export args
    # are handled.
    def prepare_compile(self):
        ''' prepare_compile() - following parent Commandsim's run() flow'''
        self.set_tool_defines()
        self.write_eda_config_and_args()

        self.slang_command_lists = self.get_compile_command_lists()
        self.write_slang_sh()

    def compile(self):
        pass

    def elaborate(self):
        ''' elaborate() - following parent Commandsim's run() flow, runs slang_command_lists'''
        if self.args['stop-before-compile'] or \
           self.args['stop-after-compile']:
            return
        self.run_commands_check_logs(self.slang_command_lists)

    def get_compile_command_lists(self) -> list:
        '''Returns list of util.ShellCommandList, for slang we'll run this in elaborate()'''

        command_list = [self.slang_exe]

        if self.args['tidy']:
            if not shutil.which(self.slang_tidy_exe):
                util.warning("Running tool slang with --tidy, but 'slang-tidy'",
                             "not in PATH, using 'slang' instead")
            else:
                command_list = [self.slang_tidy_exe]

        if self.args['hier']:
            if self.args['tidy']:
                util.warning('Running with --tidy and --heir, will attempt to use slang-hier')
            elif not shutil.which(self.slang_hier_exe):
                util.warning("Running tool slang with --hier, but 'slang-hier'",
                             "not in PATH, using 'slang' instead")
            else:
                command_list = [self.slang_hier_exe]

        config_compile_args = self.tool_config.get('compile-args', '--single-unit').split()
        command_list += config_compile_args

        command_list += self.args['slang-args'] # add user args.
        if self.args.get('slang-json', False) and command_list[0] == 'slang':
            for arg in self.all_json_args:
                if arg not in command_list:
                    command_list.append(arg)
                    if arg == '--ast-json': # needs filename
                        command_list.append('slang.json')

        # incdirs
        for value in self.incdirs:
            command_list += [ '--include-directory', value ]

        # defines:
        for k,v in self.defines.items():
            command_list.append( '--define-macro' )
            if v is None:
                command_list.append( k )
            else:
                # Generally we should only support int and str python types passed as
                # --define-macro {k}={v}
                command_list.append( f'{k}={sanitize_defines_for_sh(v)}' )

        # Because many elab target-name won't match the --top needed for
        # slang, we'll leave this to arg --slang-top:
        if self.args.get('slang-top', None):
            command_list += [ '--top', self.args['slang-top'] ]


        command_list += self.files_sv + self.files_v

        command_list = util.ShellCommandList(command_list, tee_fpath='compile.log')
        return [command_list]

    def write_slang_sh(self):
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_slang.sh',
                                      command_lists=self.slang_command_lists, line_breaks=True)


class ToolSurelog(Tool):
    _TOOL = 'surelog'
    _EXE = 'surelog'
    _URL = 'https://github.com/chipsalliance/Surelog'

    def get_versions(self) -> str:
        self.surelog_exe = ''
        if self._VERSION:
            return self._VERSION
        path = shutil.which(self._EXE)
        if not path:
            self.error(f'"{self._EXE}" not in path, need to get it ({self._URL})')
        else:
            self.surelog_exe = path

        version_ret = subprocess.run([self.surelog_exe, '--version'], capture_output=True)
        stdout = version_ret.stdout.decode('utf-8')
        util.debug(f'{path=} {version_ret=}')
        words = stdout.split() # VERSION: 1.84 (first line)
        if len(words) < 2:
            self.error(f'{self.surelog_exe} --version: returned unexpected string {version_ret=}')
        version = words[1]
        ver_list = version.split('.')
        if len(ver_list) < 2:
            self.error(f'{self.surelog_exe} --version: returned unexpected string {version_ret=} {version=}')
        self._VERSION = version
        return self._VERSION

    def set_tool_defines(self):
        self.defines['OC_TOOL_SURELOG'] = None # add define
        if 'SYNTHESIS' not in self.defines:
            self.defines['SIMULATION'] = None # add define
        # Expected to manually add SYNTHESIS command line or target, otherwise.
        # Similarly, you could use --tool slang_yosys for a synthesis friendly
        # elab in Yosys.


class CommandElabSurelog(CommandElab, ToolSurelog):
    def __init__(self, config:dict):
        CommandElab.__init__(self, config)
        ToolSurelog.__init__(self, config=self.config)
        self.args.update({
            'surelog-top': '',
        })

        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

        self.surelog_command_lists = []


    # Note that we follow parent class CommandSim's do_it() flow, that way --export args
    # are handled.
    def prepare_compile(self):
        ''' prepare_compile() - following parent Commandsim's run() flow'''
        self.set_tool_defines()
        self.write_eda_config_and_args()

        self.surelog_command_lists = self.get_compile_command_lists()
        self.write_surelog_sh()

    def compile(self):
        pass

    def elaborate(self):
        ''' elaborate() - following parent Commandsim's run() flow, runs slang_command_lists'''
        if self.args['stop-before-compile'] or \
           self.args['stop-after-compile']:
            return
        self.run_commands_check_logs(self.surelog_command_lists)

    def get_compile_command_lists(self) -> list:
        '''Returns list of util.ShellCommandList, for surelog we'll run this in elaborate()'''
        command_list = [
            self.surelog_exe
        ]

        config_compile_args = self.tool_config.get(
            'compile-args',
            '-parse').split()
        command_list += config_compile_args

        if util.args.get('debug', None) or \
           util.args.get('verbose', None):
            command_list.append('-verbose')

        # incdirs
        for value in self.incdirs:
            command_list.append('+incdir+' + value)

        # defines:
        for k,v in self.defines.items():
            if v is None:
                command_list.append( f'+define+{k}' )
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}
                command_list.append( f'+define+{k}={sanitize_defines_for_sh(v)}' )

        # Because many elab target-name won't match the --top needed for
        # slang, we'll leave this to arg --surelog-top:
        if self.args.get('surelog-top', None):
            command_list += [ '--top-module', self.args['surelog-top'] ]

        for vfile in self.files_v:
            command_list += [ '-v', vfile ]
        for svfile in self.files_sv:
            command_list += [ '-sv', svfile]

        command_list = util.ShellCommandList(command_list, tee_fpath='compile.log')
        return [command_list]

    def write_surelog_sh(self):
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_surelog.sh',
                                      command_lists=self.surelog_command_lists, line_breaks=True)


class ToolVivado(Tool):
    _TOOL = 'vivado'
    _EXE = 'vivado'
    def __init__(self, config: dict = {}):
        self.vivado_year = None
        self.vivado_release = None
        super().__init__(config=config) # calls self.get_versions()
        self.args['xilinx'] = False
        self.args['part'] = 'xcu200-fsgd2104-2-e'


    def get_versions(self) -> str:
        self.vivado_base_path = ''
        self.vivado_exe = ''
        if self._VERSION:
            return self._VERSION

        path = shutil.which(self._EXE)
        if not path:
            self.error(f"Vivado not in path, need to install or add to $PATH (looked for '{self._EXE}')")
        else:
            self.vivado_exe = path
            self.vivado_base_path, _ = os.path.split(path)

        xilinx_vivado = os.environ.get('XILINX_VIVADO')
        if not xilinx_vivado or \
           os.path.abspath(os.path.join(xilinx_vivado, 'bin', 'vivado')) != os.path.abspath(self.vivado_exe):
            util.info(f"environment for XILINX_VIVADO is not set or doesn't match the vivado path: {xilinx_vivado=}")

        version = None
        # Note this is commented out b/c it's a bit slow, up to 1.0 second to
        # run their tool just to query the version information.
        # Do this if you need the extra minor version like 2024.2.1.
        #try:
        #    # Get version from vivado -version, or xsim --version:
        #    vivado_ret = subprocess.run(['vivado', '-version'], capture_output=True)
        #    lines = vivado_ret.stdout.decode('utf-8').split('\n')
        #    words = lines[0].split() # vivado v2024.2.1 (64-bit)
        #    version = words[1][1:] # 2024.2.1
        #    self._VERSION = version
        #except:
        #    pass

        if not version:
            # Get version based on install path name:
            util.debug(f"vivado path = {self.vivado_exe}")
            m = re.search(r'(\d\d\d\d)\.(\d)', self.vivado_exe)
            if m:
                version = m.group(1) + '.' + m.group(2)
                self._VERSION = version
            else:
                self.error("Vivado path doesn't specificy version, expecting (dddd.d)")

        if version:
            numbers_list = version.split('.')
            self.vivado_year = int(numbers_list[0])
            self.vivado_release = int(numbers_list[1])
            self.vivado_version = float(numbers_list[0] + '.' + numbers_list[1])
        else:
            self.error(f"Vivado version not found, vivado path = {self.vivado__exe}")
        return self._VERSION

    # we wait to call this as part of do_it because we only want to run all this after all options
    # have been processed, as things like --xilinx will affect the defines.  Maybe it should be
    # broken into a tool vs library phase, but likely command line opts can also affect tools...
    def set_tool_defines(self):
        # Will only be called from an object which also inherits from CommandDesign, i.e. has self.defines
        self.defines['OC_TOOL_VIVADO'] = None
        self.defines['OC_TOOL_VIVADO_%4d_%d' % (self.vivado_year, self.vivado_release)] = None
        if self.args['xilinx']:
            self.defines['OC_LIBRARY_ULTRASCALE_PLUS'] = None
            self.defines['OC_LIBRARY'] = "1"
        else:
            self.defines['OC_LIBRARY_BEHAVIORAL'] = None
            self.defines['OC_LIBRARY'] = "0"
        # Code can be conditional on Vivado versions and often keys of "X or older" ...
        if (self.vivado_version <= 2021.1): self.defines['OC_TOOL_VIVADO_2021_1_OR_OLDER'] = None
        if (self.vivado_version <= 2021.2): self.defines['OC_TOOL_VIVADO_2021_2_OR_OLDER'] = None
        if (self.vivado_version <= 2022.1): self.defines['OC_TOOL_VIVADO_2022_1_OR_OLDER'] = None
        if (self.vivado_version <= 2022.2): self.defines['OC_TOOL_VIVADO_2022_2_OR_OLDER'] = None
        if (self.vivado_version <= 2023.1): self.defines['OC_TOOL_VIVADO_2023_1_OR_OLDER'] = None
        if (self.vivado_version <= 2023.2): self.defines['OC_TOOL_VIVADO_2023_2_OR_OLDER'] = None
        if (self.vivado_version <= 2024.1): self.defines['OC_TOOL_VIVADO_2024_1_OR_OLDER'] = None
        if (self.vivado_version <= 2024.2): self.defines['OC_TOOL_VIVADO_2024_2_OR_OLDER'] = None
        # ... or "X or newer" ...
        if (self.vivado_version >= 2021.1): self.defines['OC_TOOL_VIVADO_2021_1_OR_NEWER'] = None
        if (self.vivado_version >= 2021.2): self.defines['OC_TOOL_VIVADO_2021_2_OR_NEWER'] = None
        if (self.vivado_version >= 2022.1): self.defines['OC_TOOL_VIVADO_2022_1_OR_NEWER'] = None
        if (self.vivado_version >= 2022.2): self.defines['OC_TOOL_VIVADO_2022_2_OR_NEWER'] = None
        if (self.vivado_version >= 2023.1): self.defines['OC_TOOL_VIVADO_2023_1_OR_NEWER'] = None
        if (self.vivado_version >= 2023.2): self.defines['OC_TOOL_VIVADO_2023_2_OR_NEWER'] = None
        if (self.vivado_version >= 2024.1): self.defines['OC_TOOL_VIVADO_2024_1_OR_NEWER'] = None
        if (self.vivado_version >= 2024.2): self.defines['OC_TOOL_VIVADO_2024_2_OR_NEWER'] = None
        # Our first tool workaround.  Older Vivado's don't correctly compare types in synthesis (sim seems OK, argh)
        if (self.vivado_version < 2023.2): self.defines['OC_TOOL_BROKEN_TYPE_COMPARISON'] = None
        util.debug(f"Setup tool defines: {self.defines}")


class CommandSimVivado(CommandSim, ToolVivado):


    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = False
        self.args['tcl-file'] = "sim.tcl"
        self.args['fpga'] = ""
        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

        self.sim_libraries = self.tool_config.get('sim-libraries', [])


    def set_tool_defines(self):
        ToolVivado.set_tool_defines(self)

    # We do not override CommandSim.do_it(), CommandSim.check_logs_for_errors(...)


    def prepare_compile(self):
        self.set_tool_defines()
        self.xvlog_commands = self.get_compile_command_lists()
        self.xelab_commands = self.get_elaborate_command_lists()
        self.xsim_commands = self.get_simulate_command_lists()

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='compile.sh',
                                      command_lists=self.xvlog_commands)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='elaborate.sh',
                                      command_lists=self.xelab_commands)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='simulate.sh',
                                      command_lists=self.xsim_commands)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='all.sh',
                                      command_lists = [
                                          ['./pre_compile_dep_shell_commands.sh'],
                                          ['./compile.sh'],
                                          ['./elaborate.sh'],
                                          ['./simulate.sh'],
                                      ])

        util.write_eda_config_and_args(dirpath=self.args['work-dir'], command_obj_ref=self)

    def compile(self):
        if self.args['stop-before-compile']:
            return
        self.run_commands_check_logs(self.xvlog_commands, check_logs=True, log_filename='xvlog.log')

    def elaborate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile']:
            return
        # In this flow, we need to run compile + elaborate separately (unlike ModelsimASE)
        self.run_commands_check_logs(self.xelab_commands, check_logs=True, log_filename='xelab.log',
                                     must_strings=['Built simulation snapshot snapshot'])

    def simulate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            return
        self.run_commands_check_logs(self.xsim_commands, check_logs=True, log_filename='xsim.log')

    def get_compile_command_lists(self) -> list():
        self.set_tool_defines()
        ret = list()

        # compile verilog
        if len(self.files_v) or self.args['xilinx']:
            command_list = [ os.path.join(self.vivado_base_path, 'xvlog') ]
            if util.args['verbose']: command_list += ['-v', '2']
            if self.args['xilinx']:
                # Get the right glbl.v for the vivado being used.
                glbl_v = self.vivado_base_path.replace('bin', 'data/verilog/src/glbl.v')
                if not os.path.exists(glbl_v):
                    self.error(f"Could not find file {glbl_v=}")
                command_list.append(glbl_v)
            for value in self.incdirs:
                command_list.append('-i')
                command_list.append(value)
            for key in self.defines.keys():
                value = self.defines[key]
                command_list.append('-d')
                if value == None:    command_list.append(key)
                elif "\'" in value:  command_list.append("\"%s=%s\"" % (key, value))
                else:                command_list.append("\'%s=%s\'" % (key, value))
            command_list += self.args['compile-args']
            command_list += self.files_v
            ret.append(command_list)

        # compile systemverilog
        if len(self.files_sv):
            command_list = [ os.path.join(self.vivado_base_path, 'xvlog') ]
            command_list += self.tool_config.get('compile-args', '-sv').split()
            if util.args['verbose']: command_list += ['-v', '2']
            for value in self.incdirs:
                command_list.append('-i')
                command_list.append(value)
            for key in self.defines.keys():
                value = self.defines[key]
                command_list.append('-d')
                if value == None:    command_list.append(key)
                elif "\'" in value:  command_list.append("\"%s=%s\"" % (key, value))
                else:                command_list.append("\'%s=%s\'" % (key, value))
            command_list += self.args['compile-args']
            command_list += self.files_sv
            ret.append(command_list)

        return ret # list of lists

    def get_elaborate_command_lists(self):
        # elab into snapshot
        command_list = [
            os.path.join(self.vivado_base_path, 'xelab'),
            self.args['top']
        ]
        command_list += self.tool_config.get('elab-args',
                                             '-s snapshot -timescale 1ns/1ps --stats').split()
        if self.tool_config.get('elab-waves-args', ''):
            command_list += self.tool_config.get('elab-waves-args', '').split()
        elif self.args['gui'] and self.args['waves']: command_list += ['-debug', 'all']
        elif self.args['gui']: command_list += ['-debug', 'typical']
        elif self.args['waves']: command_list += ['-debug', 'wave']
        if util.args['verbose']: command_list += ['-v', '2']
        if self.args['xilinx']:
            self.sim_libraries += self.args['sim-library'] # Add any command line libraries
            for x in self.sim_libraries:
                command_list += ['-L', x]
            command_list += ['glbl']
        command_list += self.args['elab-args']
        return [command_list]

    def get_simulate_command_lists(self):
        # create TCL
        tcl_name = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        with open( tcl_name, 'w' ) as fo:
            if self.args['waves']:
                if self.args['waves-start']:
                    print("run %d ns" % self.args['waves-start'], file=fo)
                print("log_wave -recursive *", file=fo)
            print("run -all", file=fo)
            if not self.args['gui']:
                print("exit", file=fo)

        sv_seed = str(self.args['seed'])

        assert type(self.args["sim-plusargs"]) is list, \
            f'{self.target=} {type(self.args["sim-plusargs"])=} but must be list'

        # xsim uses: --testplusarg foo=bar
        xsim_plusargs_list = list()
        for x in self.args['sim-plusargs']:
            xsim_plusargs_list.append('--testplusarg')
            if x[0] == '+':
                x = x[1:]
            xsim_plusargs_list.append(f'\"{x}\"')

        # execute snapshot
        command_list = [ os.path.join(self.vivado_base_path, 'xsim') ]
        command_list += self.tool_config.get('simulate-args', 'snapshot --stats').split()
        if self.args['gui']: command_list += ['-gui']
        command_list += [
            '--tclbatch', tcl_name,
            "--sv_seed", sv_seed
        ]
        command_list += xsim_plusargs_list
        command_list += self.args['sim-args']
        return [command_list] # single command



class CommandElabVivado(CommandSimVivado):
    def __init__(self, config:dict):
        CommandSimVivado.__init__(self, config)
        # add args specific to this simulator
        self.args['stop-after-elaborate'] = True


class CommandSynthVivado(CommandSynth, ToolVivado):
    def __init__(self, config:dict):
        CommandSynth.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = False
        self.args['tcl-file'] = "synth.tcl"
        self.args['xdc'] = ""
        self.args['fpga'] = ""

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()
        if self.is_export_enabled():
            self.do_export()
            return self.status

        # create TCL
        tcl_file = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        v = ""
        if util.args['verbose']: v += " -verbose"
        elif util.args['quiet']: v += " -quiet"
        defines = ""
        for key in self.defines.keys():
            value = self.defines[key]
            defines += (f"-verilog_define {key}" + (" " if value == None else f"={value} "))
        incdirs = ""
        if len(self.incdirs):
            incdirs = " -include_dirs "+";".join(self.incdirs)
        flatten = ""
        if self.args['flatten-all']:    flatten = "-flatten_hierarchy full"
        elif self.args['flatten-none']: flatten = "-flatten_hierarchy none"
        with open( tcl_file, 'w' ) as fo:
            for f in self.files_v:     print(f"read_verilog {f}", file=fo)
            for f in self.files_sv:    print(f"read_verilog -sv {f}", file=fo)
            for f in self.files_vhd:   print(f"add_file {f}", file=fo)
            if self.args['xdc'] != "":
                default_xdc = False
                xdc_file = os.path.abspath(self.args['xdc'])
            else:
                default_xdc = True
                xdc_file = os.path.abspath(os.path.join(self.args['work-dir'], "default_constraints.xdc"))
                util.info(f"Creating default constraints: clock:",
                          f"{self.args['clock-name']}, {self.args['clock-ns']} (ns),",
                          f"idelay:{self.args['idelay-ns']}, odelay:{self.args['odelay-ns']}")
                with open( xdc_file, 'w' ) as ft:
                    clock_name = self.args['clock-name']
                    period = self.args['clock-ns']
                    name_not_equal_clocks_str = f'NAME !~ "{clock_name}"'
                    print(f"create_clock -add -name {clock_name} -period {period} [get_ports " \
                          + "{" + clock_name + "}]", file=ft)
                    print(f"set_input_delay -max {self.args['idelay-ns']} -clock {clock_name} " +
                          "[get_ports * -filter {DIRECTION == IN && " + name_not_equal_clocks_str + "}]",
                          file=ft)
                    print(f"set_output_delay -max {self.args['odelay-ns']} -clock {clock_name} " +
                          "[get_ports * -filter {DIRECTION == OUT}]",
                          file=ft)

            print(f"create_fileset -constrset constraints_1 {v}", file=fo)
            print(f"add_files -fileset constraints_1 {xdc_file} {v}", file=fo)
            print(f"# FIRST PASS -- auto_detect_xpm", file=fo)
            print(f"synth_design -rtl -rtl_skip_ip -rtl_skip_constraints -no_timing_driven -no_iobuf "+
                  f"-top {self.args['top']} {incdirs} {defines} {v}", file=fo)
            print(f"auto_detect_xpm {v}", file=fo)
            print(f"synth_design -no_iobuf -part {self.args['part']} {flatten} -constrset constraints_1 "+
                  f"-top {self.args['top']} {incdirs} {defines} {v}", file=fo)
            print(f"write_verilog -force {self.args['top']}.vg {v}", file=fo)
            print(f"report_utilization -file {self.args['top']}.flat.util.rpt {v}", file=fo)
            print(f"report_utilization -file {self.args['top']}.hier.util.rpt {v} -hierarchical -hierarchical_depth 20", file=fo)
            print(f"report_timing -file {self.args['top']}.timing.rpt {v}", file=fo)
            print(f"report_timing_summary -file {self.args['top']}.summary.timing.rpt {v}", file=fo)
            print(f"report_timing -from [all_inputs] -file {self.args['top']}.input.timing.rpt {v}", file=fo)
            print(f"report_timing -to [all_outputs] -file {self.args['top']}.output.timing.rpt {v}", file=fo)
            print(f"report_timing -from [all_inputs] -to [all_outputs] -file {self.args['top']}.through.timing.rpt {v}", file=fo)
            print(f"set si [get_property -quiet SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup -from [all_inputs]]]", file=fo)
            print(f"set so [get_property -quiet SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup -to [all_outputs]]]", file=fo)
            print(f"set_false_path -from [all_inputs] {v}", file=fo)
            print(f"set_false_path -to [all_outputs] {v}", file=fo)
            print(f"set sf [get_property -quiet SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]", file=fo)
            print(f"if {{ ! [string is double -strict $sf] }} {{ set sf 9999 }}", file=fo)
            print(f"if {{ ! [string is double -strict $si] }} {{ set si 9999 }}", file=fo)
            print(f"if {{ ! [string is double -strict $so] }} {{ set so 9999 }}", file=fo)
            print(f"puts \"\"", file=fo)
            print(f"puts \"*** ****************** ***\"", file=fo)
            print(f"puts \"***                    ***\"", file=fo)
            print(f"puts \"*** SYNTHESIS COMPLETE ***\"", file=fo)
            print(f"puts \"***                    ***\"", file=fo)
            print(f"puts \"*** ****************** ***\"", file=fo)
            print(f"puts \"\"", file=fo)
            print(f"puts \"** AREA **\"", file=fo)
            print(f"report_utilization -hierarchical", file=fo)
            print(f"puts \"** TIMING **\"", file=fo)
            print(f"puts \"\"", file=fo)
            if default_xdc:
                print(f"puts \"(Used default XDC: {xdc_file})\"", file=fo)
                print(f"puts \"DEF CLOCK NS  : [format %.3f {self.args['clock-ns']}]\"", file=fo)
                print(f"puts \"DEF IDELAY NS : [format %.3f {self.args['idelay-ns']}]\"", file=fo)
                print(f"puts \"DEF ODELAY NS : [format %.3f {self.args['odelay-ns']}]\"", file=fo)
            else:
                print(f"puts \"(Used provided XDC: {xdc_file})\"", file=fo)
            print(f"puts \"\"", file=fo)
            print(f"puts \"F2F SLACK     : [format %.3f $sf]\"", file=fo)
            print(f"puts \"INPUT SLACK   : [format %.3f $si]\"", file=fo)
            print(f"puts \"OUTPUT SLACK  : [format %.3f $so]\"", file=fo)
            print(f"puts \"\"", file=fo)

        # execute Vivado
        command_list = [ self.vivado_exe, '-mode', 'batch', '-source', tcl_file, '-log', f"{self.args['top']}.synth.log" ]
        if not util.args['verbose']: command_list.append('-notrace')
        self.exec(self.args['work-dir'], command_list)


class CommandProjVivado(CommandProj, ToolVivado):
    def __init__(self, config:dict):
        CommandProj.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = True
        self.args['oc-vivado-tcl'] = True
        self.args['tcl-file'] = "proj.tcl"
        self.args['xdc'] = ""
        self.args['board'] = ""

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        # create TCL
        tcl_file = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        v = ""
        if util.args['verbose']: v += " -verbose"
        elif util.args['quiet']: v += " -quiet"

        with open( tcl_file, 'w' ) as fo:

            print(f"create_project {self.args['top']}_proj {self.args['work-dir']} {v}", file=fo)

            oc_root = util.get_oc_root()
            if self.args['oc-vivado-tcl'] and oc_root:
                print(f"source \"{oc_root}/boards/vendors/xilinx/oc_vivado.tcl\" -notrace", file=fo)
            if self.args['board'] != "":
                print(f"set_property board_part {self.args['board']} [current_project]", file=fo)

            incdirs = " ".join(self.incdirs)
            defines = ""
            for key in self.defines.keys():
                value = self.defines[key]
                defines += (f"{key} " if value == None else f"{key}={value} ")

            print(f"set_property include_dirs {{{incdirs}}} [get_filesets sources_1]", file=fo)
            print(f"set_property include_dirs {{{incdirs}}} [get_filesets sim_1]", file=fo)
            print(f"set_property verilog_define {{{defines}}} [get_filesets sources_1]", file=fo)
            print(f"set_property verilog_define {{SIMULATION {defines}}} [get_filesets sim_1]", file=fo)

            print(f"set_property -name {{STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS}} -value {{-verilog_define SYNTHESIS}} "+
                  f"-objects [get_runs synth_1]", file=fo)
            print(f"set_property {{xsim.simulate.runtime}} {{10ms}} [get_filesets sim_1]", file=fo)
            print(f"set_property {{xsim.simulate.log_all_signals}} {{true}} [get_filesets sim_1]", file=fo)

            for f in self.files_v + self.files_sv + self.files_vhd:
                if f.find("/sim/") >= 0: fileset = "sim_1"
                elif f.find("/tests/") >= 0: fileset = "sim_1"
                else: fileset = "sources_1"
                print(f"add_files -norecurse {f} -fileset [get_filesets {fileset}]", file=fo)

        # execute Vivado
        command_list = [ self.vivado_exe, '-mode', 'gui', '-source', tcl_file, '-log', f"{self.args['top']}.proj.log" ]
        if not util.args['verbose']: command_list.append('-notrace')
        self.exec(self.args['work-dir'], command_list)
        util.info(f"Synthesis done, results are in: {self.args['work-dir']}")


class CommandBuildVivado(CommandBuild, ToolVivado):
    def __init__(self, config:dict):
        CommandBuild.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = False
        self.args['fpga'] = ""
        self.args['proj'] = False
        self.args['reset'] = False

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        # create FLIST
        flist_file = os.path.join(self.args['work-dir'],'build.flist')
        util.debug(f"CommandBuildVivado: {self.args['top-path']=}")

        eda_path = get_eda_exec('flist')
        command_list = [
            eda_path, 'flist',
            '--tool', self.args['tool'],
            self.args['top-path'],
            '--force',
            '--xilinx',
            '--out', flist_file,
            '--no-emit-incdir',
            '--no-single-quote-define', # Needed to run in Command.exec( ... shell=False)
            '--no-quote-define',
            # on --prefix- items, use shlex.quote(str) so spaces work with subprocess shell=False:
            '--prefix-define', shlex.quote("oc_set_project_define "),
            '--prefix-sv', shlex.quote("add_files -norecurse "),
            '--prefix-v', shlex.quote("add_files -norecurse "),
            '--prefix-vhd', shlex.quote("add_files -norecurse "),
        ]
        for key,value in self.defines.items():
            if value is None:   command_list += [ f"+define+{key}" ]
            else:               command_list += [ shlex.quote(f"+define+{key}={value}") ]
        cwd = util.getcwd()


        # Write out a .sh command, but only for debug, it is not run.
        command_list = util.ShellCommandList(command_list, tee_fpath='run_eda_flist.log')
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_eda_flist.sh',
                                      command_lists=[command_list], line_breaks=True)

        self.exec(cwd, command_list, tee_fpath=command_list.tee_fpath)

        if self.args['job-name'] == "":
            self.args['job-name'] = self.args['design']
        project_dir = 'project.'+self.args['job-name']

        # launch Vivado
        command_list = [self.vivado_exe]
        command_list += ['-mode', 'gui' if self.args['gui'] else 'batch' ]
        command_list += ['-log', os.path.join(self.args['work-dir'], self.args['top']+'.build.log') ]
        if not util.args['verbose']: command_list.append('-notrace')
        command_list += ['-source', self.args['build-script'] ]
        command_list += ['-tclargs', project_dir, flist_file] # these must come last, all after -tclargs get passed to build-script
        if self.args['proj']: command_list += ['--proj']
        if self.args['reset']: command_list += ['--reset']

        # Write out a .sh command, but only for debug, it is not run.
        command_list = util.ShellCommandList(command_list, tee_fpath=None)
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='run_vivado.sh',
                                      command_lists=[command_list], line_breaks=True)

        self.exec(cwd, command_list, tee_fpath=command_list.tee_fpath)
        util.info(f"Build done, results are in: {self.args['work-dir']}")


class CommandFListVivado(CommandFList, ToolVivado):
    def __init__(self, config:dict):
        CommandFList.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)


class CommandUploadVivado(CommandUpload, ToolVivado):
    def __init__(self, config:dict):
        CommandUpload.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = False
        self.args['file'] = False
        self.args['usb'] = True
        self.args['host'] = "localhost"
        self.args['port'] = 3121
        self.args['target'] = 0
        self.args['tcl-file'] = "upload.tcl"

    def do_it(self):
        if self.args['file'] == False:
            util.info(f"Searching for bitfiles...")
            found_file = False
            all_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(".bit"):
                        found_file = os.path.abspath(os.path.join(root,file))
                        util.info(f"Found bitfile: {found_file}")
                        all_files.append(found_file)
            self.args['file'] = found_file
        if len(all_files) > 1:
            all_files.sort(key=lambda f: os.path.getmtime(f))
            self.args['file'] = all_files[-1]
            util.info(f"Choosing: {self.args['file']} (newest)")
        if self.args['file'] == False:
            self.error(f"Couldn't find a bitfile to upload")
        if self.args['usb']:
            util.info(f"Uploading bitfile: {self.args['file']}")
            util.info(f"Uploading via {self.args['host']}:{self.args['port']} USB target #{self.args['target']}")
            self.upload_usb_jtag(self.args['host'], self.args['port'], self.args['target'], self.args['file'])
        else:
            self.error(f"Only know how to upload via USB for now")
        self.write_eda_config_and_args()

    def upload_usb_jtag(self, host, port, target, bit_file):
        # create TCL
        tcl_file = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        ltx_file = os.path.splitext(bit_file)[0] + ".ltx"
        if not os.path.exists(ltx_file):
            ltx_file = False

        with open( tcl_file, 'w' ) as fo:
            print(f"open_hw", file=fo)
            print(f"connect_hw_server -url {host}:{port}", file=fo)
            print(f"refresh_hw_server -force_poll", file=fo)
            print(f"set hw_targets [get_hw_targets */xilinx_tcf/Xilinx/*]", file=fo)
            print(f"if {{ [llength $hw_targets] <= {target} }} {{", file=fo)
            print(f"  puts \"ERROR: There is no target number {target}\"", file=fo)
            print(f"}}", file=fo)
            print(f"current_hw_target [lindex $hw_targets {target}]", file=fo)
            print(f"open_hw_target", file=fo)
            print(f"refresh_hw_target", file=fo)
            print(f"current_hw_device [lindex [get_hw_devices] 0]", file=fo)
            print(f"refresh_hw_device [current_hw_device]", file=fo)
            print(f"set_property PROGRAM.FILE {bit_file} [current_hw_device]", file=fo)
            if ltx_file:
                print(f"set_property PROBES.FILE {ltx_file} [current_hw_device]", file=fo)
            print(f"program_hw_devices [current_hw_device]", file=fo)
            if self.args['gui']:
                print(f"refresh_hw_device [current_hw_device]", file=fo)
                print(f"display_hw_ila_data [ get_hw_ila_data hw_ila_data_1 -of_objects [get_hw_ilas] ]", file=fo)
            else:
                print(f"close_hw_target", file=fo)
                print(f"exit", file=fo)

        # execute Vivado
        command_list = [ self.vivado_exe, '-source', tcl_file, '-log', f"fpga.upload.log" ]
        if not self.args['gui']:
            command_list.append('-mode')
            command_list.append('batch')
        self.exec(self.args['work-dir'], command_list)

class CommandOpenVivado(CommandOpen, ToolVivado):
    def __init__(self, config:dict):
        CommandOpen.__init__(self, config)
        ToolVivado.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = True
        self.args['file'] = False

    def do_it(self):
        if self.args['file'] == False:
            util.info(f"Searching for project...")
            found_file = False
            all_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(".xpr"):
                        found_file = os.path.abspath(os.path.join(root,file))
                        util.info(f"Found project: {found_file}")
                        all_files.append(found_file)
            self.args['file'] = found_file
        if len(all_files) > 1:
            all_files.sort(key=lambda f: os.path.getmtime(f))
            self.args['file'] = all_files[-1]
            util.info(f"Choosing: {self.args['file']} (newest)")
        if self.args['file'] == False:
            self.error(f"Couldn't find an XPR Vivado project to open")
        projname = os.path.splitext(os.path.basename(self.args['file']))[0]
        projdir = os.path.dirname(self.args['file'])
        oc_root = util.get_oc_root()
        oc_vivado_tcl = os.path.join(oc_root, 'boards', 'vendors', 'xilinx', 'oc_vivado.tcl')
        command_list = [ self.vivado_exe, '-source', oc_vivado_tcl, '-log', f"{projname}.open.log", self.args['file'] ]
        self.write_eda_config_and_args()
        self.exec(projdir, command_list)


class ToolQuesta(Tool):
    _TOOL = 'questa'
    _EXE = 'qrun'
    def __init__(self, config: dict = {}):
        self.questa_major = None
        self.questa_minor = None
        super().__init__(config=config)
        self.args['xilinx'] = False
        self.args['part'] = 'xcu200-fsgd2104-2-e'

    def get_versions(self) -> str:
        if self._VERSION:
            return self._VERSION
        self.starter_edition = False # Aka, modelsim_ase
        self.sim_exe = '' # vsim or qrun
        self.sim_exe_base_path = ''
        path = shutil.which(self._EXE)
        if not path:
            self.error(f"{self._EXE} not in path, need to setup (i.e. source /opt/intelFPGA_pro/23.4/settings64.sh")
            util.debug(f"path = %s" % path)
            if self._EXE.endswith('qrun') and 'modelsim_ase' in path:
                util.warning(f"{self._EXE=} Questa path is for starter edition (modelsim_ase),",
                             "consider using --tool modelsim_ase")
        else:
            self.sim_exe = path
            self.sim_exe_base_path, _ = os.path.split(path)

        if self._EXE.endswith('vsim'):
            self.starter_edition = True

        m = re.search(r'(\d+)\.(\d+)', path)
        if m:
            self.questa_major = int(m.group(1))
            self.questa_minor = int(m.group(2))
            self._VERSION = str(self.questa_major) + '.' + str(self.questa_minor)
        else:
            self.error(f"Questa path doesn't specificy version, expecting (d+.d+)")
        return self._VERSION

    def set_tool_defines(self):
        # Will only be called from an object which also inherits from CommandDesign, i.e. has self.defines
        self.defines['OC_TOOL_QUESTA'] = None
        self.defines['OC_TOOL_QUESTA_%d_%d' % (self.questa_major, self.questa_minor)] = None
        if self.args['xilinx']:
            self.defines['OC_LIBRARY_ULTRASCALE_PLUS'] = None
            self.defines['OC_LIBRARY'] = "1"
        else:
            self.defines['OC_LIBRARY_BEHAVIORAL'] = None
            self.defines['OC_LIBRARY'] = "0"

class CommandSimQuesta(CommandSim, ToolQuesta):
    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolQuesta.__init__(self, config=self.config)
        # add args specific to this simulator
        self.args['gui'] = False
        self.args['tcl-file'] = "sim.tcl"
        self.shell_command = self.sim_exe # set by ToolQuesta.get_versions(self)
        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

    def set_tool_defines(self):
        ToolQuesta.set_tool_defines(self)

    def do_it(self):
        # add defines for this job
        self.set_tool_defines()
        self.write_eda_config_and_args()

        # it all gets done with one command
        command_list = [ self.shell_command, "-64", "-sv" ]

        # incdirs
        for value in self.incdirs:
            command_list += [ f"+incdir+{value}" ]

        # defines
        for key in self.defines.keys():
            value = self.defines[key]
            if value == None:
                command_list += [ f"+define+{key}" ]
            elif type(value) is str and "\'" in value:
                command_list += [ f"\"+define+{key}={value}\"" ]
            else:
                command_list += [ f"\'+define+{key}={value}\'" ]

        # compile verilog
        for f in self.files_v:
            command_list += [ f ]

        # compile systemverilog
        for f in self.files_sv:
            command_list += [ f ]

        if self.args['xilinx']:
            glbl_v = self.vivado_base_path.replace('bin', 'data/verilog/src/glbl.v')
            if not os.path.exists(glbl_v):
                self.error(f"Vivado is not setup, could not find file {glbl_v=}")
            command_list.append(glbl_v)

        # misc options
        command_list += [ '-top', self.args['top'], '-timescale', '1ns/1ps', '-work', 'work.lib']
        command_list += [
            # otherwise lots of warnings about defaulting to "var" which isn't LRM behavior, and we don't need it
            '-svinputport=net',
            #  Existing package 'xxxx_pkg' at line 9 will be overwritten.
            '-suppress', 'vlog-2275',
            #  Extra checking for conflict in always_comb and always_latch variables is done at vopt time
            '-suppress', 'vlog-2583',
            #  Missing connection for port 'xxxx' (The default port value will be used)
            '-suppress', 'vopt-13159',
            #  Too few port connections for 'uAW_FIFO'.  Expected 10, found 8
            '-suppress', 'vopt-2685',
            #  Missing connection for port 'almostEmpty' ... unfortunately same message for inputs and outputs... :(
            '-note', 'vopt-2718',
        ]
        if self.args['gui']: command_list += ['-gui=interactive', '+acc', '-i']
        elif self.args['waves']: command_list += ['+acc', '-c']
        else: command_list += ['-c']
        if util.args['verbose']: command_list += ['-verbose']
        if self.args['xilinx']:
            # this will need some work
            self.error("THIS ISN'T GOING TO WORK, got --xilinx with Questa which isn't ready yet", do_exit=False)
            # command_list += "-L xil_defaultlib -L unisims_ver -L unimacro_ver -L xpm -L secureip -L xilinx_vip".split(" ")

        # check if we're bailing out early
        if self.args['stop-after-elaborate']:
            command_list += ['-elab', 'elab.output', '-do', '"quit"' ]

        # create TCL
        tcl_name = os.path.abspath(os.path.join(self.args['work-dir'], self.args['tcl-file']))
        with open( tcl_name, 'w' ) as fo:
            if self.args['waves']:
                if self.args['waves-start']:
                    print("run %d ns" % self.args['waves-start'], file=fo)
                print("add wave -r /*", file=fo)
            print("run -all", file=fo)
            if not self.args['gui']:
                print("quit", file=fo)
        command_list += ['-do', tcl_name ]

        # execute snapshot
        self.exec(self.args['work-dir'], command_list)


class CommandElabQuesta(CommandSimQuesta):
    def __init__(self, config:dict):
        CommandSimQuesta.__init__(self, config)
        # add args specific to this simulator
        self.args['stop-after-elaborate'] = True

class ToolModelsimAse(ToolQuesta):
    _TOOL = 'modelsim_ase' # otherwise it's 'questa' from base class.
    _EXE = 'vsim'

class CommandSimModelsimAse(CommandSim, ToolModelsimAse):
    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolQuesta.__init__(self, config=self.config)
        self.shell_command = os.path.join(self.sim_exe_base_path, 'vsim')
        self.starter_edition = True
        self.args.update({
            'tool': self._TOOL, # override
            'gui': False,
        })
        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

    def set_tool_defines(self):
        # Update any defines from config.tools.modelsim_ase:
        self.defines.update(
            self.tool_config.get(
                'defines',
                # defaults, if not set:
                {'OC_ASSERT_PROPERTY_NOT_SUPPORTED': 1,
                 'OC_TOOL_MODELSIM_ASE': 1}
            )
        )

    # We do override do_it() to avoid using CommandSimQuesta.do_it()
    def do_it(self):
        CommandSim.do_it(self)
        #    self.compile()   # runs if stop-before-compile is False, stop-after-compile is True
        #    self.elaborate() # runs if stop-before-compile is False, stop-after-compile is False, stop-after-elaborate is True
        #    self.simulate()  # runs if stop-* are all False (run the whole thing)


    def prepare_compile(self):
        self.set_tool_defines()
        self.write_vlog_dot_f()
        self.write_vsim_dot_do(dot_do_to_write='all')
        if self.args['xilinx']:
            self.error('Error: --xilinx with Modelsim ASE is not yet supported', do_exit=False)

        vsim_command_lists = self.get_compile_command_lists()
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='compile_only.sh',
                                      command_lists=vsim_command_lists)

        vsim_command_lists = self.get_elaborate_command_lists()
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='compile_elaborate_only.sh',
                                      command_lists=vsim_command_lists)

        vsim_command_lists = self.get_simulate_command_lists()
        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='all.sh',
                                      command_lists = \
                                      [['./pre_compile_dep_shell_commands.sh']] + vsim_command_lists)

        util.write_eda_config_and_args(dirpath=self.args['work-dir'], command_obj_ref=self)

    def compile(self):
        if self.args['stop-before-compile']:
            # don't run anything, save everyting we've already run in _prep_compile()
            return
        if self.args['stop-after-compile']:
            vsim_command_lists = self.get_compile_command_lists()
            self.run_commands_check_logs(vsim_command_lists, log_filename='sim.log')

    def elaborate(self):
        if self.args['stop-before-compile']:
            return
        if self.args['stop-after-compile']:
            return
        if self.args['stop-after-elaborate']:
        # only run this if we stop after elaborate (simulate run it all)
            vsim_command_lists = self.get_elaborate_command_lists()
            self.run_commands_check_logs(vsim_command_lists, log_filename='sim.log')

    def simulate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            # don't run this if we're stopping before/after compile/elab
            return
        vsim_command_lists = self.get_simulate_command_lists()
        self.run_commands_check_logs(vsim_command_lists, log_filename='sim.log')

    def get_compile_command_lists(self):
        # This will also set up a compile.
        vsim_command_list = [
            self.sim_exe,
            '' if self.args['gui'] else '-c',
            '-do', 'vsim_vlogonly.do', '-logfile', 'sim.log',
        ]
        return [vsim_command_list]

    def get_elaborate_command_lists(self):
        # This will also set up a compile, for vlog + vsim (0 time)
        vsim_command_list = [
            self.sim_exe,
            '' if self.args['gui'] else '-c',
            '-do', 'vsim_lintonly.do', '-logfile', 'sim.log',
        ]
        return [vsim_command_list]

    def get_simulate_command_lists(self):
    # This will also set up a compile, for vlog + vsim (with run -a)
        vsim_command_list = [
            self.sim_exe,
            '' if self.args['gui'] else '-c',
            '-do', 'vsim.do', '-logfile', 'sim.log',
        ]
        return [vsim_command_list]


    def write_vlog_dot_f(self, filename='vlog.f'):
        vlog_dot_f_lines = list()

        # Add compile args from config.tool.modelsim_ase:
        vlog_dot_f_lines += self.tool_config.get(
            'compile-args',
            '-sv -svinputport=net -lint').split()
        # Add waivers from config.tool.modelsim_ase:
        for waiver in self.tool_config.get(
                'compile-waivers',
                [ #defaults:
                    '2275', # 2275 - Existing package 'foo_pkg' will be overwritten.
                ]):
            vlog_dot_f_lines += ['-suppress', str(waiver)]

        vlog_dot_f_fname = filename
        vlog_dot_f_fpath = os.path.join(self.args['work-dir'], vlog_dot_f_fname)

        for value in self.incdirs:
            vlog_dot_f_lines += [ f"+incdir+{value}" ]

        for k,v in self.defines.items():
            if v is None:
                vlog_dot_f_lines += [ f'+define+{k}' ]
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}, but also for SystemVerilog plusargs
                vlog_dot_f_lines += [ f'+define+{k}={sanitize_defines_for_sh(v)}' ]


        vlog_dot_f_lines += self.args['compile-args']

        vlog_dot_f_lines += [
            '-source',
            ] + list(self.files_sv) + list(self.files_v)

        assert len(self.files_sv) + len(self.files_v) > 0, \
            f'{self.target=} {self.files_sv=} and {self.files_v=} are empty, cannot create a valid vlog.f'

        with open(vlog_dot_f_fpath, 'w') as f:
            f.writelines(line + "\n" for line in vlog_dot_f_lines)

    def write_vsim_dot_do(self, dot_do_to_write : list()):
        '''Writes files(s) based on dot_do_to_write(list, values [] or with items 'all', 'sim', 'lint', 'vlog'.'''

        vsim_dot_do_fname = 'vsim.do'
        vsim_dot_do_fpath = os.path.join(self.args['work-dir'], vsim_dot_do_fname)

        vsim_lintonly_dot_do_fname = 'vsim_lintonly.do'
        vsim_lintonly_dot_do_fpath = os.path.join(self.args['work-dir'], vsim_lintonly_dot_do_fname)

        vsim_vlogonly_dot_do_fname = 'vsim_vlogonly.do'
        vsim_vlogonly_dot_do_fpath = os.path.join(self.args['work-dir'], vsim_vlogonly_dot_do_fname)

        sv_seed = self.args['seed']

        sim_plusargs = list()
        for x in self.args['sim-plusargs']:
            # For vsim we need to add a +key=value if the + is missing
            if x[0] != '+':
                x = f'+{x}'
            sim_plusargs.append(x)

        sim_plusargs_str = ' '.join(sim_plusargs)

        assert type(self.args["sim-plusargs"]) is list, \
            f'{self.target=} {type(self.args["sim-plusargs"])=} but must be list'

        vsim_suppress_list = list()
        # Add waivers from config.tool.modelsim_ase:
        for waiver in self.tool_config.get(
                'simulate-waivers', [
                    #defaults:
                    '3009', # 3009: [TSCALE] - Module 'foo' does not have a timeunit/timeprecision
                            #       specification in effect, but other modules do.
                ]):
            vsim_suppress_list += ['-suppress', str(waiver)]

        vsim_suppress_list_str = ' '.join(vsim_suppress_list)

        voptargs_str = ""
        if self.args['gui'] or self.args['waves']:
            voptargs_str = self.tool_config.get('simulate-waves-args', '+acc')

        # TODO(drew): support self.args['sim_libary', 'elab-args', sim-args'] (3 lists) to add to vsim_one_liner.

        vsim_one_liner = "vsim -onfinish stop " \
            + f"-sv_seed {sv_seed} {sim_plusargs_str} {vsim_suppress_list_str} {voptargs_str} work.{self.args['top']}"

        vsim_one_liner = vsim_one_liner.replace('\n', ' ') # needs to be a one-liner

        vsim_vlogonly_dot_do_lines = [
            "if {[file exists work]} { vdel -all work; }",
            "vlib work;",
            "if {[catch {vlog -f vlog.f} result]} {",
            "    echo \"Caught $result \";",
            "    if {[batch_mode]} {",
            "        quit -f -code 20;",
            "    }",
            "}",
            "if {[batch_mode]} {",
            "    quit -f -code 0;",
            "}",
        ]

        vsim_lintonly_dot_do_lines = [
            "if {[file exists work]} { vdel -all work; }",
            "vlib work;",
            "quietly set qc 30;",
            "if {[catch {vlog -f vlog.f} result]} {",
            "    echo \"Caught $result \";",
            "    if {[batch_mode]} {",
            "        quit -f -code 20;",
            "    }",
            "}",
            "if {[catch { " + vsim_one_liner + " } result] } {",
            "    echo \"Caught $result\";",
            "    if {[batch_mode]} {",
            "        quit -f -code 19;",
            "    }",
            "}",
            "set TestStatus [coverage attribute -name SEED -name TESTSTATUS];",
            "if {[regexp \"TESTSTATUS += 0\" $TestStatus]} {",
            "    quietly set qc 0;",
            "} elseif {[regexp \"TESTSTATUS += 1\" $TestStatus]} {",
            "    quietly set qc 0;",
            "} else {",
            "    quietly set qc 2;",
            "}",
            "if {[batch_mode]} {",
            "    quit -f -code $qc;",
            "}",
        ]

        vsim_dot_do_lines = [
            "if {[file exists work]} { vdel -all work; }",
            "vlib work;",
            "quietly set qc 30;",
            "if {[catch {vlog -f vlog.f} result]} {",
            "    echo \"Caught $result \";",
            "    if {[batch_mode]} {",
            "        quit -f -code 20;",
            "    }",
            "}",
            "if {[catch { " + vsim_one_liner + " } result] } {",
            "    echo \"Caught $result\";",
            "    if {[batch_mode]} {",
            "        quit -f -code 19;",
            "    }",
            "}",
            "onbreak { resume; };",
            "catch {log -r *};",
            "run -a;",
            "set TestStatus [coverage attribute -name SEED -name TESTSTATUS];",
            "if {[regexp \"TESTSTATUS += 0\" $TestStatus]} {",
            "    quietly set qc 0;",
            "} elseif {[regexp \"TESTSTATUS += 1\" $TestStatus]} {",
            "    quietly set qc 0;",
            "} else {",
            "    quietly set qc 2;",
            "}",
            "if {[batch_mode]} {",
            "    quit -f -code $qc;",
            "}",
        ]

        write_all = len(dot_do_to_write) == 0 or 'all' in dot_do_to_write
        if write_all or 'sim' in dot_do_to_write:
            with open(vsim_dot_do_fpath, 'w') as f:
                f.writelines(line + "\n" for line in vsim_dot_do_lines)

        if write_all or 'lint' in dot_do_to_write:
            with open(vsim_lintonly_dot_do_fpath, 'w') as f:
                f.writelines(line + "\n" for line in vsim_lintonly_dot_do_lines)

        if write_all or 'vlog' in dot_do_to_write:
            with open(vsim_vlogonly_dot_do_fpath, 'w') as f:
                f.writelines(line + "\n" for line in vsim_vlogonly_dot_do_lines)



class CommandElabModelsimAse(CommandSimModelsimAse):
    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True


class ToolIverilog(Tool):
    _TOOL = 'iverilog'
    _EXE = 'iverilog'
    _URL = 'https://github.com/steveicarus/iverilog'

    def get_versions(self) -> str:
        self.iverilog_exe = ''
        if self._VERSION:
            return self._VERSION

        iverilog_path = shutil.which(self._EXE)
        if iverilog_path is None:
            self.error(f'"{self._EXE}" not in path, need to get it ({self._URL})')
        else:
            self.iverilog_exe = iverilog_path

        iverilog_version_ret = subprocess.run([self.iverilog_exe, '-v'], capture_output=True)
        lines = iverilog_version_ret.stdout.decode("utf-8").split('\n')
        words = lines[0].split() # 'Icarus Verilog version 13.0 (devel) (s20221226-568-g62727e8b2)'
        version = words[3]
        util.debug(f'{iverilog_path=} {lines[0]=}')
        ver_list = version.split('.')
        self._VERSION = version
        return self._VERSION

    def set_tool_defines(self):
        self.defines.update({
            'SIMULATION': 1,
            'IVERILOG': 1,
            'OC_ASSERT_PROPERTY_NOT_SUPPORTED': 1,
        })


class CommandSimIverilog(CommandSim, ToolIverilog):
    def __init__(self, config:dict):
        CommandSim.__init__(self, config)
        ToolIverilog.__init__(self, config=self.config)
        self.args['gui'] = False
        self.args['tcl-file'] = None
        self.set_tool_config_from_config() # Sets self.tool_config from self.config (--config-yml=YAML)

        self.args_help.update({
            'waves':    'Include waveforms, if possible for iverilog by applying' \
            + ' exe runtime arg +trace. User will need SV code to interpret the plusarg' \
            + ' and apply $dumpfile("dump.vcd") or another non-vcd file extension.',
        })


    def set_tool_defines(self):
        ToolIverilog.set_tool_defines(self)

    # We do not override CommandSim.do_it()
    def prepare_compile(self):
        self.set_tool_defines()
        if self.args['xilinx']:
            self.error('Error: --xilinx with Iverilog is not yet supported', do_exit=False)

        self.iverilog_command_lists = self.get_compile_command_lists()
        self.iverilog_exec_command_lists  = self.get_simulate_command_lists()

        paths = ['logs']
        util.safe_mkdirs(base=self.args['work-dir'], new_dirs=paths)

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='compile_only.sh',
                                      command_lists=self.iverilog_command_lists, line_breaks=True)

        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='simulate_only.sh',
                                      command_lists = self.iverilog_exec_command_lists)


        util.write_shell_command_file(dirpath=self.args['work-dir'], filename='all.sh',
                                      command_lists = [
                                          ['./pre_compile_dep_shell_commands.sh'],
                                          ['./compile_only.sh'],
                                          ['./simulate_only.sh'],
                                      ])

        util.write_eda_config_and_args(dirpath=self.args['work-dir'], command_obj_ref=self)

    def compile(self):
        if self.args['stop-before-compile']:
            return
        self.run_commands_check_logs(self.iverilog_command_lists, check_logs=False)

    def elaborate(self):
        pass

    def simulate(self):
        if self.args['stop-before-compile'] or self.args['stop-after-compile'] or \
           self.args['stop-after-elaborate']:
            # don't run this if we're stopping before/after compile/elab
            return

        # Note that this is not returning a pass/fail bash return code,
        # so we will likely have to log-scrape to deterimine pass/fail.
        self.run_commands_check_logs(self.iverilog_exec_command_lists)

    def get_compile_command_lists(self):

        command_list = [
            self.iverilog_exe,
        ]
        command_list += self.tool_config.get(
            'compile-args',
            '-gsupported-assertions -grelative-include').split()
        command_list += [
            '-s', self.args['top'],
            '-o', 'sim.exe',
        ]

        if util.args['verbose']:
            command_list += ['-v']

        # incdirs
        for value in self.incdirs:
            command_list += [ '-I', value ]

        for k,v in self.defines.items():
            if v is None:
                command_list += [ '-D', k ]
            else:
                # Generally we should only support int and str python types passed as
                # +define+{k}={v}, but also for SystemVerilog plusargs
                command_list += [ '-D', f'{k}={sanitize_defines_for_sh(v)}' ]

        assert len(self.files_sv) + len(self.files_v) > 0, \
            f'{self.target=} {self.files_sv=} and {self.files_v=} are empty, cannot call iverilog'

        command_list += list(self.files_sv) + list(self.files_v)

        return [ util.ShellCommandList(command_list) ]

    def get_simulate_command_lists(self):

        # Need to return a list-of-lists, even though we only have 1 command
        cmd_list = ['./sim.exe']
        cmd_list += self.tool_config.get('simulate-args', '').split()
        if self.args['waves']:
            cmd_list += self.tool_config.get('simulate-waves-args', '').split()
        return [ util.ShellCommandList(cmd_list, tee_fpath='sim.log') ]


class CommandElabIverilog(CommandSimIverilog):
    def __init__(self, config:dict):
        super().__init__(config)
        self.args['stop-after-elaborate'] = True



# ****************************************************************************************************
# MAIN

# Set config['command_handler'] entries for (command, Class) so we know which
# eda command (such as, command: eda sim) is handled by which class (such as class: CommandSim)
# These are also overriden depending on the tool, for example --tool verilator sets
# "sim": CommandSimVerilator.
def init_config(config: dict,  quiet=False, tool=None) -> dict:
    '''Sets or clears entries in config (dict) so tools can be re-loaded.'''

    # If config didn't set the auto_tools_order, then use a fully populated default
    # dict:
    config = eda_config.get_config_merged_with_defaults(config)

    config['command_handler'] = {
        "sim"         : CommandSim,
        "elab"        : CommandElab,
        "synth"       : CommandSynth,
        "flist"       : CommandFList,
        "proj"        : CommandProj,
        "multi"       : CommandMulti,
        "tools-multi" : CommandToolsMulti,
        "sweep"       : CommandSweep,
        "build"       : CommandBuild,
        "waves"       : CommandWaves,
        "upload"      : CommandUpload,
        "open"        : CommandOpen,
        "export"      : CommandExport,
    }

    config['auto_tools_found'] = dict()
    config['tools_loaded'] = set()
    config = auto_tool_setup(config=config, quiet=quiet, tool=tool)
    return config


def print_base_help() -> None:
    '''Prints help() information from other argparsers we use, without "usage"'''
    # using bare 'print' here, since help was requested, avoids --color and --quiet
    print(util.get_argparser_short_help())
    print(eda_config.get_argparser_short_help())
    print(get_argparser_short_help())


def usage(tokens: list, config: dict, command=""):
    '''Returns an int shell return code, given remaining args (tokens list) and eda command.

    config is the config dict. Used to check valid commands in config['command_handler']

    Note that we pass the command (str) if possible, so things like:
     > eda help sim --tool verilator
    Will still return this message. This allows args like --config-yml=<file> to work with
    the help message if command is blank, such as:
     > eda --config-yml=<file> help
    '''

    if command == "":
        print(
"""
Usage:
    eda [<options>] <command> [options] <files|targets, ...>

Where <command> is one of:

    sim          - Simulates a DEPS target
    elab         - Elaborates a DEPS target (sort of sim based LINT)
    synth        - Synthesizes a DEPS target
    flist        - Create dependency from a DEPS target
    proj         - Create a project from a DEPS target for GUI sim/waves/debug
    multi        - Run multiple DEPS targets, serially or in parallel
    tools-multi  - Same as 'multi' but run on all available tools, or specfied using --tools
    sweep        - Sweep one or more arguments across a range, serially or in parallel
    build        - Build for a board, creating a project and running build flow
    waves        - Opens waveform from prior simulation
    upload       - Uploads a finished design into hardware
    open         - Opens a project
    export       - Export files related to a target, tool independent
    help         - This help (without args), or i.e. "eda help sim" for specific help

And <files|targets, ...> is one or more source file or DEPS markup file target,
    such as .v, .sv, .vhd[l], .cpp files, or a target key in a DEPS.[yml|yaml|toml|json].
    Note that you can prefix source files with `sv@`, `v@`, `vhdl@` or `cpp@` to
    force use that file as systemverilog, verilog, vhdl, or C++, respectively.

"""
        )
        print_base_help()
        return 0
    elif command in config['command_handler'].keys():
        sco = config['command_handler'][command](config=config) # sub command object
        sco.help(tokens=tokens)
        return util.exit(0)
    else:
        util.info(f"Valid commands are: ")
        for k in sorted(config['command_handler'].keys()):
            util.info(f"   {k:20}")
        return util.error(f"Cannot provide help, don't understand command: '{command}'")

def interactive(config: dict):
    read_file = False
    while True:
        if read_file:
            line = f.readline()
            if line:
                print("%s->%s" % (fname, line), end="")
            else:
                read_file = False
                f.close()
                continue
        else:
            line = input('EDA->')
        m = re.match(r'^([^\#]*)\#.*$', line)
        if m: line = m.group(1)
        tokens = line.split()
        original_args = tokens.copy()
        # NOTE: interactive will not correctly handle --config-yml arg (from eda_config.py),
        # but we should do a best effor to re-parse args from util.py, such as
        # --quiet, --color, --fancy, --logfile, --debug or --debug-level, etc
        _, tokens = util.process_tokens(tokens)
        process_tokens(tokens=tokens, original_args=original_args, config=config, interactive=True)


def get_eda_exec(command:str=''):
    # NOTE(drew): This is kind of flaky. 'eda multi' reinvokes 'eda'. But the executable for 'eda'
    # is one of:
    # 1. pip3 install opencos-eda
    #    -- script 'eda', installed from PyPi
    # 2. pip3 uninstall .; python3 -m build; pip3 install
    #    -- script 'eda' but installed from local.
    # 2. (opencos repo)/bin/eda - a python wrapper to link to (opencos repo)/opencos/eda.py (package)
    #    packages cannot be run standalone, they need to be called as: python3 -m opencos.eda,
    #    and do not work with relative paths. This only works if env OC_ROOT is set or can be found.
    # 3. If you ran 'source bin/addpath' then you are always using the local (opencos repo)/bin/eda
    eda_path = shutil.which('eda')
    if not eda_path:
        # Can we run from OC_ROOT/bin/eda?
        oc_root = util.get_oc_root()
        if not oc_root:
            util.error(f"Need 'eda' in our path to run 'eda {command}', could not find env OC_ROOT, {eda_path=}, {oc_root=}")
        else:
            bin_eda = os.path.join(oc_root, 'bin', 'eda')
            if not os.path.exists(bin_eda):
                util.error(f"Need 'eda' in our path to run 'eda {command}', cound not find bin/, {eda_path=}, {oc_root=}, {bin_eda=}")
            else:
                util.info(f"'eda' not in path, using {bin_eda=} for 'eda' {command} executable")
                eda_path = os.path.abspath(bin_eda)

    return eda_path



def auto_tool_setup(warnings:bool=True, config=None, quiet=False, tool=None) -> dict:
    '''Returns an updated config, uses config['auto_tools_order'][0] dict, calls tool_setup(..)

    -- adds items to config['tools_loaded'] set
    -- updates config['command_handler'][command] with a Tool class

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'
      If so, updates config['auto_tools_order'][tool]['exe']
    '''
    import importlib.util

    tool = eda_config.update_config_auto_tool_order_for_tool(
        tool=tool, config=config
    )

    assert 'auto_tools_order' in config
    assert type(config['auto_tools_order']) is list
    assert type(config['auto_tools_order'][0]) is dict

    for name, value in config['auto_tools_order'][0].items():
        if tool and tool != name:
            continue # if called with tool=(some_name), then only load that tool.

        exe = value.get('exe', str())
        if type(exe) is list:
            exe_list = exe
        elif type(exe) is str:
            exe_list = [exe] # make it a list
        else:
            util.error(f'eda.py: config["auto_tools_order"][0] for {name=} {value=} has bad type for {exe=}')
            continue

        has_all_py = True
        requires_py_list = value.get('requires_py', list())
        for pkg in requires_py_list:
            spec = importlib.util.find_spec(pkg)
            if not spec:
                has_all_py = False

        has_all_env = True
        requires_env_list = value.get('requires_env', list())
        for env in requires_env_list:
            if not os.environ.get(env, ''):
                has_all_env = False

        has_all_exe = True
        for exe in exe_list:
            assert exe != '', f'{tool=} {value=} value missing "exe" {exe=}'
            p = shutil.which(exe)
            if not p:
                has_all_exe = False

        if has_all_exe:
            requires_cmd_list = value.get('requires_cmd', list())
            for cmd in requires_cmd_list:
                cmd_list = shlex.split(cmd)
                try:
                    proc = subprocess.run(cmd_list, capture_output=True, input=b'exit\n\n')
                    if proc.returncode != 0:
                        if not quiet:
                            util.debug(f"For tool {name} missing required command ({proc.returncode=}): {cmd_list=}")
                        has_all_exe = False
                except:
                    has_all_exe = False


        if all([has_all_py, has_all_env, has_all_exe]):
            exe = exe_list[0]
            p = shutil.which(exe)
            config['auto_tools_found'][name] = exe # populate key-value pairs w/ first exe in list
            if not quiet:
                util.info(f"Detected {name} ({p}), auto-setting up tool {name}")
            tool_setup(tool=name, quiet=True, auto_setup=True, warnings=warnings, config=config)

    return config


def tool_setup(tool: str, config: dict, quiet: bool = False, auto_setup: bool = False,
               warnings: bool = True):
    ''' Adds items to config["tools_loaded"] (set) and updates config['command_handler'].

    config is potentially updated for entry ['command_handler'][command] with a Tool class.

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'

    '''
    import importlib

    tool = eda_config.update_config_auto_tool_order_for_tool(
        tool=tool, config=config
    )

    if not quiet and not auto_setup:
        util.info(f"Setup for tool: '{tool}'")

    if not tool:
        return

    if tool not in config['auto_tools_order'][0]:
        tools = list(config.get('auto_tools_order', [{}])[0].keys())
        cfg_yaml_fname = config.get('config-yml', None)
        util.error(f"Don't know how to run tool_setup({tool=}), is not in",
                   f"config['auto_tools_order'] for {tools=}",
                   f"from {cfg_yaml_fname}")
        return

    if tool not in config['auto_tools_found']:
        cfg_yaml_fname = config.get('config-yml', None)
        util.error(f"Don't know how to run tool_setup({tool=}), is not in",
                   f"{config['auto_tools_found']=} from {cfg_yaml_fname}")
        return

    if auto_setup and tool is not None and tool in config['tools_loaded']:
        # Do I realy need to warn if a tool was loaded from auto_tool_setup(),
        # but then I also called it via --tool verilator? Only warn if auto_setup=True:
        if warnings:
            util.warning(f"tool_setup: {auto_setup=} already setup for {tool}?")

    entry = config['auto_tools_order'][0].get(tool, dict())
    tool_cmd_handler_dict = entry.get('handlers', dict())

    for command, str_class_name in tool_cmd_handler_dict.items():
        current_handler_cls = config['command_handler'].get(command, None)
        ext_mod = None

        if auto_setup and current_handler_cls is not None and issubclass(current_handler_cls, Tool):
            # If we're not in auto_setup, then always override (aka arg --tool=<this tool>)
            # skip, already has a tool associated with it, and we're in auto_setup=True
            continue

        if str_class_name not in globals():
            cls = util.import_class_from_string(str_class_name)
        else:
            cls = globals().get(str_class_name, None)

        assert issubclass(cls, Tool), f'{str_class_name=} is does not have Tool class associated with it'
        util.debug(f'Setting {cls=} for {command=} in config.command_handler')
        config['command_handler'][command] = cls

    config['tools_loaded'].add(tool)


def which_tool(command, config):
    '''Returns which tool will be used for a command, given the command_handlers in config dict.'''
    from opencos import eda_tool_helper
    if config is None:
        util.error(f'which_tool({command=}) called w/out config')
    if not command in config.get('command_handler', {}):
        util.error("which_tool called with invalid command?")

    # Note: we could create a throw-away Command object using config, and check its
    # args['tool']:
    #    cmd_obj = config['command_handler'][command](config=config)
    #    return cmd_obj.args.get('tool', None)
    # But that has side effects and prints a lot of garbage, and does a lot
    # of loading and setting values to create that throw away Command object.

    # Instead, we'll directly look up at the class _TOOL w/out creating the obj.
    tool = getattr(config['command_handler'][command], '_TOOL', None)
    return tool


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='eda options', add_help=False, allow_abbrev=False)
    parser.add_argument('-q', '--quit', action='store_true',
                        help='For interactive mode (eda called with no options, command, or targets)')
    parser.add_argument('--exit', action='store_true', help='same as --quit')
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('--tool', type=str, default=None,
                        help='Tool to use for this command, such as: modelsim_ase, verilator,' \
                        + ' modelsim_ase=/path/to/bin/vsim, verilator=/path/to/bin/verilator')
    parser.add_argument('--eda-safe', action='store_true',
                        help='disable all DEPS file deps shell commands, overrides values from --config-yml')
    return parser

def get_argparser_short_help() -> str:
    return util.get_argparser_short_help(parser=get_argparser())


def process_tokens(tokens: list, original_args: list, config: dict, interactive=False):
    # this is the top level token processing function.  tokens can come from command line, setup file, or interactively.
    # we do one pass through all the tokens, triaging them into:
    # - those we can execute immediate (help, quit, and global opens like --debug, --color)
    # - a command (sim, synth, etc)
    # - command arguments (--seed, +define, +incdir, etc) which will be deferred and processed by the command

    deferred_tokens = []
    command = ""

    parser = get_argparser()
    try:
        parsed, unparsed = parser.parse_known_args(tokens + [''])
        unparsed = list(filter(None, unparsed))
    except argparse.ArgumentError:
        return util.error(f'problem attempting to parse_known_args for {tokens=}')

    config['tool'] = parsed.tool

    # We support a few way of handling quit, exit, or --quit, --exit, -q
    if parsed.quit or parsed.exit or 'exit' in unparsed or 'quit' in unparsed:
        return util.exit(0)
    if parsed.help or 'help' in unparsed:
        if 'help' in unparsed:
            # We'll figure out the command first before applying help, so
            # usage(tokens, config, command) doesn't have a custom argparser guessing.
            unparsed.remove('help')
            parsed.help = True
    if parsed.eda_safe:
        eda_config.update_config_for_eda_safe(config)

    if not interactive:
        # Run init_config() now, we deferred it in main(), but only run it
        # for this tool (or tool=None to figure it out)
        config = init_config(config, tool=parsed.tool)
        if not config:
            util.error(f'eda.py main: problem loading config, {args=}')
            return 3


    util.debug(f'eda process_tokens: {parsed=} {unparsed=}')
    for value in unparsed:
        if value in config['command_handler'].keys():
            command = value
            unparsed.remove(value)
            break

    # Deal with help, now that we have the command (if it was set).
    if parsed.help:
        if not command:
            # if we didn't find the command in config['command_handler'], and
            # since we're entering help anyway (will exit) set command to the
            # first unparsed word looking arg:
            for arg in unparsed:
                if not arg.startswith('-'):
                    command = arg
        return usage(tokens=unparsed, config=config, command=command)

    if parsed.tool:
        tool_setup(parsed.tool, config=config)

    deferred_tokens = unparsed
    if command == "":
        util.error("Didn't get a command!")
        return 1

    sco = config['command_handler'][command](config=config) # sub command object
    util.debug(f'{command=}')
    util.debug(f'{sco.config=}')
    util.debug(f'{type(sco)=}')
    if not parsed.tool:
        use_tool = which_tool(command, config)
        util.info(f"--tool not specified, using default for {command=}: {use_tool}")

    check_command_handler_cls(command_obj=sco, command=command, parsed_args=parsed)

    # Add the original, nothing-parsed args to the Command.config dict.
    sco.config['eda_original_args'] = original_args

    setattr(sco, 'command_name', command) # as a safeguard, b/c 'command' is not always passed to 'sco'
    sco.process_tokens(deferred_tokens)

    # Rather than trust all implementations of sco.process_tokens(..) return status, simply
    # query it from the Command object:
    rc = getattr(sco, 'status', 1)
    util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=}')
    return rc


def check_command_handler_cls(command_obj:object, command:str, parsed_args):
    sco = command_obj
    for cls in getattr(sco, 'CHECK_REQUIRES', []):
        if not isinstance(sco, cls):
            # If someone set --tool verilator for command=synth, then our 'sco' will have defaulted
            # to CommandSynth with no tool attached. If we don't have a tool set, error and return.
            util.warning(f"{command=} is using handling class '{type(sco)}' (but missing",
                         f"requirement {cls}, likely because we aren't using a derived class",
                         "for a specific tool)")
            return util.error(f"EDA {command=} for tool '{parsed_args.tool}' is not",
                              f"supported (this tool '{parsed_args.tool}' cannot run {command=})")


def sanitize_defines_for_sh(value):
    # Need to sanitize this for shell in case someone sends a +define+foo+1'b0,
    # which needs to be escaped as +define+foo+1\'b0, otherwise bash or sh will
    # think this is an unterminated string.
    # TODO(drew): decide if we should instead us shlex.quote('+define+key=value')
    # instead of this function.
    if type(value) is str:
        value = value.replace("'", "\\" + "'")
    return value

# **************************************************************
# **** Interrupt Handler

def signal_handler(sig, frame):
    util.fancy_stop()
    util.info('Received Ctrl+C...', start='\nINFO: [EDA] ')
    util.exit(-1)

# **************************************************************
# **** Startup Code


def main(*args):
    ''' Returns return code (int), entry point for calling eda.main(*list) directly in py code'''

    args = list(args)
    if len(args) == 0:
        # If not one passed args, then use sys.argv:
        args = sys.argv[1:]

    original_args = args.copy() # save before any parsing.

    # Set global --debug, --quiet, --color  early before parsing other args:
    util_parsed, unparsed = util.process_tokens(args)

    util.debug(f"main: file: {os.path.realpath(__file__)}")
    util.debug(f"main: args: {args=}")

    if util_parsed.version:
        # Do not consider parsed.quiet, print the version and exit:
        print(f'eda {opencos.__version__} ({opencos.__pyproject_name__})')
        sys.exit(0)

    if not util.args['quiet']:
        util.info(f'eda: version {opencos.__version__}')

    # Handle --config-yml= arg
    config, unparsed = eda_config.get_eda_config(unparsed)


    # Note - we used to call: config = init_config(config=config)
    # However, we now defer calling init_config(..) until eda.process_tokens(..)

    util.info("*** OpenCOS EDA ***")

    if len(args) == 0 or (len(args) == 1 and '--debug' in args):
        # special snowflake case if someone called with a singular arg --debug
        # (without --help or exit)
        util.debug(f"Starting automatic tool setup: init_config()")
        config = init_config(config=config)
        if not config:
            util.error(f'eda.py main: problem loading config, {args=}')
            return 3
        return interactive(config=config)
    else:
        return process_tokens(tokens=list(unparsed), original_args=original_args,
                              config=config)


def main_cli(support_respawn=False):
    ''' Returns None, will exit with return code. Entry point for package script or __main__.'''

    if support_respawn and '--no-respawn' not in sys.argv:
        # If someone called eda.py directly (aka, __name__ == '__main__'),
        # then we still support a legacy mode of operation - where we check
        # for OC_ROOT (in env, or git repo) to make sure this is the right
        # location of eda.py by calling main_cli(support_respawn=True).
        # Otherwise, we do not respawn $OC_ROOT/bin/eda.py
        # Can also be avoided with --no-respawn.

        # Note - respawn will never work if calling as a package executable script,
        # which is why our package entrypoint will be main_cli() w/out support_respawn.
        main_maybe_respawn()


    signal.signal(signal.SIGINT, signal_handler)
    util.global_exit_allowed = True
    # Strip eda or eda.py from sys.argv, we know who we are if called from __main__:
    rc = main()
    util.exit(rc)


def main_maybe_respawn():
    ''' Returns None, will respawn - run - exit, or will return and the command

    is expected to run in main_cli()'''

    # First we check if we are respawning
    this_path = os.path.realpath(__file__)
    if debug_respawn: util.info(f"RESPAWN: this_path : '{this_path}'")
    oc_root = util.get_oc_root()
    if debug_respawn: util.info(f"RESPAWN: oc_root   : '{oc_root}'")
    cwd = util.getcwd()
    if debug_respawn: util.info(f"RESPAWN: cwd       : '{cwd}'")
    if oc_root:
        new_paths = [
            os.path.join(oc_root, 'opencos', 'eda.py'),
            os.path.join(oc_root, 'bin', 'eda'),
        ]
        if debug_respawn: util.info(f"RESPAWN: {new_paths=} {this_path=}")
        if this_path not in new_paths and os.path.exists(new_paths[0]):
            # we are not the correct version of EDA for this Git repo, we should respawn
            util.info(f"{this_path} respawning {new_paths[0]} in {cwd} with --no-respawn")
            sys.argv[0] = new_paths[0]
            sys.argv.insert(1, '--no-respawn')
            proc = subprocess.Popen(sys.argv, shell=0, cwd=cwd, universal_newlines=True)
            while True:
                try:
                    proc.communicate()
                    break
                except KeyboardInterrupt:
                    continue
            # get exit status from proc and return it
            util.exit(proc.returncode, quiet=True)
        else:
            if debug_respawn: util.info(f"RESPAWN: {oc_root=} respawn not necessary")
    else:
        if debug_respawn: util.info("RESPAWN: respawn not necessary")


if __name__ == '__main__':
    main_cli(support_respawn=True)

# IDEAS:
# * options with no default (i.e. if user doesn't override, THEN we set it, like "seed" or "work-dir") can be given a
#   special type (DefaultVar) versus saying "None" so that help can say more about it (it's a string, it's default val
#   is X, etc) and it can be queried as to whether it's really a default val.  This avoids having to avoid default vals
#   that user can never set (-1, None, etc) which make it hard to infer the type.  this same object can be given help
#   info and simply "render" to the expected type (str, integer, etc) when used.
