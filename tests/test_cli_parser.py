"""Test for cli_parser.py."""
import pytest
import pytest_check as check

from cliconfig.cli_parser import parse


def test_parse() -> None:
    """Test for parse."""
    config_paths, config_cli_params = parse(
        ['main.py', '--config', 'config1.yaml,config2.yaml', '--a', '1', '--b=2']
    )
    check.equal(config_paths, ['config1.yaml', 'config2.yaml'])
    check.equal(config_cli_params, {'a': 1, 'b': 2})
    b_str = ("{'2': {'3': 4, '5': [6.3], '7': True, '8': Null, "
             "'9': [2, {'a': 1}]}}")
    config_paths, config_cli_params = parse(["main.py", "--a='b=c'", f"--b={b_str}"])
    val = {
        'a': 'b=c',
        'b': {'2': {'3': 4, '5': [6.3], '7': True, '8': None, '9': [2, {'a': 1}]}}
    }
    check.equal(config_paths, [])
    check.equal(config_cli_params, val)
    with pytest.raises(ValueError, match="Only one '--config ' argument is allowed.*"):
        parse(['main.py', '--config', 'config1.yaml', '--config', 'config2.yaml'])
