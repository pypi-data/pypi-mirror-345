#!/usr/bin/env python3
import yaml, toml, json
import sys, os
from opencos.deps_helpers import get_deps_markup_file

def get_markup_table_keys(partial_path='./'):
    '''Returns a list of root level keys for DEPS.[yml|yaml|toml|json]

    Does not include DEFAULTS.
    '''
    partial_target = ''
    if not partial_path or partial_path == '.':
        partial_path = './'

    if not os.path.exists(partial_path):
        partial_path, partial_target = os.path.split(partial_path)
    if not partial_path:
        partial_path = './'

    filepath = get_deps_markup_file(base_path=partial_path)
    if not filepath:
        # Couldn't find a DEPS file, let bash completion handle it (with -W words or -G glob)
        return []

    data = {}
    try:
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        elif filepath.endswith('.toml'):
            data = toml.load(filepath)
        elif filepath.endswith('.json'):
            with open(filepath) as f:
                data = json.load(f)
    except:
        pass

    if not isinstance(data, dict):
        # We found a DEPS file, but it wasn't a table/dict so we can't return root keys
        return []

    # Try to resolve path/to/target/partial_target_
    # -- prepend path information to found targets in path/to/target/DEPS
    prepend = ''
    if partial_path and partial_path != './':
        prepend = partial_path
        if not partial_path.endswith('/'):
            prepend += '/'

    # Return the list of keys w/ prepended path information, and don't include 'DEFAULTS'
    return [prepend + x for x in list(data.keys()) if x.startswith(partial_target) and x != 'DEFAULTS']


def main():
    if len(sys.argv) > 1:
        partial_path = sys.argv[1]
    else:
        partial_path = './'
    keys = get_markup_table_keys(partial_path)
    print(" ".join(keys))

if __name__ == "__main__":
    main()
