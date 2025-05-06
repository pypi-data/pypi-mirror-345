
# If you want to run this, consider running from the root of opencos repo:
#> python3 -m pytest --verbose opencos/*/*.py
# which avoids using any pip installed opencos.eda, and uses the local one
# due to "python3 -m"

import os
import sys
import pytest

from opencos import oc_cli

def test_args_help():
    rc = oc_cli.main('--help')
    print(f'{rc=}')
    assert not rc

def test_parse_names():
    oc_cli.parse_names()
    t = getattr(oc_cli, 'name_tables', None)
    assert t is not None
    assert len(t.keys()) == 7, f'Expect exactly 7 keys in t, {t=}'
    entry = t.get('OC_VENDOR', None)
    assert entry is not None
    assert len(entry.keys()) >= 1
