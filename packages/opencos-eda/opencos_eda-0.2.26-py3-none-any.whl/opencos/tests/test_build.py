

def test_version():
    from opencos import __version__
    print(f'{__version__=}')
    assert __version__
    assert __version__ != 'unknown'
    numbers = __version__.split('.')
    assert any([int(number) != 0 for number in numbers])
