from opencos.deps_schema import check_files

import os


def test_all_deps():

    # get all the files
    all_deps_files = list()
    for root, dirs, files in os.walk(os.getcwd()):
        for fname in files:
            if fname.startswith('DEPS') and \
               any([fname.endswith(x) for x in ['.yml', '.json', '.toml', 'DEPS']]):

                all_deps_files.append(os.path.join(root, fname))

    # run all the files, but one at a time:
    for fname in all_deps_files:
        passes = check_files(all_deps_files)
        assert passes, f'{fname=} did not pass schema checks'

    assert len(all_deps_files) > 0
