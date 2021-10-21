from pprint import pprint

import pytest
from pysbeorchestra import Orchestra


def test_valid():
    orchestra = Orchestra()
    orchestra.validate('tests/xml/OrchestraFIXLatest.xml')


def test_invalid():
    orchestra = Orchestra()
    with pytest.raises(ValueError):
        orchestra.validate('tests/xml/BadOrchestra.xml')


def test_to_dict():
    orchestra = Orchestra()
    with open('tests/OrchestraFIXLatest-dict.txt', 'w') as f:
        pprint(orchestra.to_dict('tests/xml/OrchestraFIXLatest.xml'), f)
        f.close


def test_from_dict():
    orchestra = Orchestra()
    with open('tests/OrchestraFIXLatest-copy.xml', 'wb') as f:
        orchestra.from_dict(orchestra.to_dict(
            'tests/xml/OrchestraFIXLatest.xml'), f)
        f.close
