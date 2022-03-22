import os

from orchestratransposer import SBE
from orchestratransposer.sbe.sbe import SBE20

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    errors = sbe.validate(xml_path)
    assert not errors


def test_invalid():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'BadExamples.xml')
    errors = sbe.validate(xml_path)
    assert errors


def test_to_dict():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = sbe.read_xml(xml_path)
        print(str(instance), file=f)
        assert not errors


def test_invalid_to_dict():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'BadExamples.xml')
    output_path = os.path.join(output_dir(), 'BadExamples-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = sbe.read_xml(xml_path)
        print(str(instance), file=f)
        assert errors


def test_to_from_xml():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples-copy.xml')
    with open(output_path, 'wb') as f:
        (instance, errors) = sbe.read_xml(xml_path)
        sbe.write_xml(instance, f)
        assert not errors


def test_valid20():
    sbe = SBE20()
    xml_path = os.path.join(XML_FILE_DIR, 'Examples20.xml')
    errors = sbe.validate(xml_path)
    assert not errors
