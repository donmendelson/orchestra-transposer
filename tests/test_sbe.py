from pprint import pprint

import pytest
from pysbeorchestra import SBE


def test_valid():
    sbe = SBE()
    sbe.validate('tests/xml/Examples.xml')

def test_invalid():
    sbe = SBE()
    with pytest.raises(ValueError):
        sbe.validate('tests/xml/BadExamples.xml')

def test_to_dict():
    sbe = SBE()
    with open('tests/Examples-dict.txt', 'w') as f:
        pprint(sbe.to_dict('tests/xml/Examples.xml'), f)
        f.close

def test_from_dict():
    sbe = SBE()
    with open('tests/Examples-copy.xml', 'wb') as f:
        sbe.from_dict(sbe.to_dict('tests/xml/Examples.xml'), f)
        f.close
