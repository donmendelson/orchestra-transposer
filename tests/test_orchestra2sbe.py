import os

from orchestratransposer import Orchestra, Orchestra2SBE
from orchestratransposer.orchestra2sbe import Orchestra2SBE10_20

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path

def test_orchestra2sbe_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples2Orchestra.xml')
    output_path = os.path.join(output_dir(), 'Examples-roundtrip.xml')
    translator = Orchestra2SBE()
    with open(output_path, 'wb') as f:
        errors = translator.orch2sbe_xml(xml_path, f)
        assert not errors


def test_orchestra2sbe_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples2Orchestra.xml')
    output_path = os.path.join(output_dir(), 'Examples-roundtrip-dict.txt')
    orchestra = Orchestra()
    (orch_instance, errors) = orchestra.read_xml(xml_path)
    translator = Orchestra2SBE()
    sbe_instance = translator.orch2sbe_dict(orch_instance)
    with open(output_path, 'w') as f:
        print(str(sbe_instance), file=f)

def test_orchestra2sbe20_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples202Orchestra.xml')
    output_path = os.path.join(output_dir(), 'Examples20-roundtrip.xml')
    translator = Orchestra2SBE10_20()
    with open(output_path, 'wb') as f:
        errors = translator.orch2sbe_xml(xml_path, f)
        assert not errors


def test_orchestra2sbe20_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples202Orchestra.xml')
    output_path = os.path.join(output_dir(), 'Examples20-roundtrip-dict.txt')
    orchestra = Orchestra()
    (orch_instance, errors) = orchestra.read_xml(xml_path)
    translator = Orchestra2SBE10_20()
    sbe_instance = translator.orch2sbe_dict(orch_instance)
    with open(output_path, 'w') as f:
        print(str(sbe_instance), file=f)

