import os
from pprint import pprint

import pytest
from pysbeorchestra import Orchestra

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    error_iter = orchestra.validate(xml_path)
    assert not next(error_iter, None)


def test_invalid():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    error_iter = orchestra.validate(xml_path)
    assert next(error_iter, None)


def test_to_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-dict.txt')
    with open(output_path, 'w') as f:
        for data in orchestra.to_dict(xml_path):
            pprint(data, f)
        f.close


def test_invalid_to_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    output_path = os.path.join(output_dir(), 'BadOrchestra-dict.txt')
    with open(output_path, 'w') as f:
        for data in orchestra.to_dict(xml_path):
            pprint(data, f)
        f.close


def test_to_from_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-copy.xml')
    with open(output_path, 'wb') as f:
        for data in orchestra.to_dict(xml_path):
            orchestra.from_dict(data, f)
        f.close
