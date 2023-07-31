import pytest
from colorclass import Color

from unbeheader.util import EXCLUDE_FILE_NAME
from unbeheader.util import cformat
from unbeheader.util import is_excluded


@pytest.mark.parametrize(('string', 'expected'), (
    ('', Color('{/all}')),
    ('%{reset}', Color('{/all}')),
    ('%{red}red', Color('{red}red{/all}')),
    ('%{grey}red', Color('{white}red{/all}')),
    ('%{red!}red', Color('{b}{red}red{/all}')),
    ('%{red,white}red', Color('{red}{bgwhite}red{/all}')),
    ('%{red,grey}red', Color('{red}{bgwhite}red{/all}')),
))
def test_cformat(string, expected):
    assert cformat(string) == expected


def test_is_excluded(tmp_path):
    assert is_excluded(str(tmp_path), str(tmp_path)) is False
    file_path = tmp_path / EXCLUDE_FILE_NAME
    file_path.touch()
    assert is_excluded(str(tmp_path), str(tmp_path)) is True


def test_is_excluded_for_nested(tmp_path):
    nested_dir_path = tmp_path / 'nested'
    nested_dir_path.mkdir()
    file_path = tmp_path / EXCLUDE_FILE_NAME
    file_path.touch()
    assert is_excluded(str(nested_dir_path), str(tmp_path)) is True
