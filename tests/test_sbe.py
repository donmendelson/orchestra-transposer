import os

import pytest
from pysbeorchestra import SBE, SBEInstance

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    error_iter = sbe.validate(xml_path)
    assert not next(error_iter, None)


def test_invalid():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'BadExamples.xml')
    error_iter = sbe.validate(xml_path)
    assert next(error_iter, None)


def test_to_dict():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = sbe.read_xml(xml_path)
        print(instance.root(), file=f)
        f.close
        assert not errors


def test_invalid_to_dict():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'BadExamples.xml')
    output_path = os.path.join(output_dir(), 'BadExamples-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = sbe.read_xml(xml_path)
        print(instance.root(), file=f)
        f.close
        assert errors


def test_to_from_dict():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples-copy.xml')
    with open(output_path, 'wb') as f:
        (instance, errors) = sbe.read_xml(xml_path)
        sbe.write_xml(instance, f)
        f.close
        assert not errors
