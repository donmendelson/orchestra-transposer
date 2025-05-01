import os
from typing import List, Tuple

from orchestratransposer.orchestra.orchestra import Orchestra11
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance11

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    """Create and return the output directory for test artifacts."""
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    """
    Test that Orchestra11 can validate a well-formed Orchestra XML file.
    Expects no validation errors when processing a valid Orchestra XML file.
    """
    orchestra = Orchestra11()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    errors = orchestra.validate(xml_path)
    assert not errors


def test_invalid():
    """
    Test that Orchestra11 correctly identifies invalid Orchestra XML.
    Expects validation errors when processing a malformed Orchestra XML file.
    """
    orchestra = Orchestra11()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    errors = orchestra.validate(xml_path)
    assert errors


def test_to_dict():
    """
    Test conversion of Orchestra XML to OrchestraInstance11 dictionary.
    Reads a valid Orchestra XML file and converts it to an OrchestraInstance11,
    then writes the string representation to a text file for inspection.
    Expects no conversion errors.
    """
    orchestra = Orchestra11()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-v11-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        print(str(instance), file=f)
        assert not errors


def test_invalid_to_dict():
    """
    Test handling of invalid Orchestra XML when converting to OrchestraInstance11.
    Attempts to read a malformed Orchestra XML file and convert it to an OrchestraInstance11,
    then writes the string representation to a text file for inspection.
    Expects conversion errors.
    """
    orchestra = Orchestra11()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    output_path = os.path.join(output_dir(), 'BadOrchestra-v11-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        print(str(instance), file=f)
        assert errors


def test_to_from_dict():
    """
    Test round-trip conversion between Orchestra XML and OrchestraInstance11.
    Reads a valid Orchestra XML file, converts it to an OrchestraInstance11,
    then writes it back to XML.
    Expects no errors during the conversion process.
    """
    orchestra = Orchestra11()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-v11-copy.xml')
    with open(output_path, 'wb') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        orchestra.write_xml(instance, f)
        assert not errors


def test_scenarios():
    """
    Test the scenarios functionality specific to Orchestra 1.1.
    Verifies that an OrchestraInstance11 can access and retrieve scenarios,
    which is a feature introduced in Orchestra 1.1.
    Expects the scenarios() method to return a list.
    """
    orchestra = Orchestra11()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    (instance, errors) = orchestra.read_xml(xml_path)
    assert not errors
    scenarios = instance.scenarios()
    assert isinstance(scenarios, list) 