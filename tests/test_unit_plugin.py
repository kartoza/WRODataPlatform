import pytest

from ckanext.wro.plugins import wro_plugin

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "raw_date, expected",
    [
        pytest.param("2022-02-23", "2022-02-23T00:00:00Z"),
        pytest.param("02-21-2022", "2022-02-21T00:00:00Z"),
        pytest.param("not a date", None),
    ],
)
def test_parse_date(raw_date, expected):
    result = wro_plugin._parse_date(raw_date)
    assert result == expected
