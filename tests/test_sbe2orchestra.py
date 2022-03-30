import os

from orchestratransposer import SBE2Orchestra, SBE
from orchestratransposer.sbe.sbe import SBE20
from orchestratransposer.sbe2orchestra import SBE2Orchestra20_10

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_sbe2orchestra_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples2Orchestra.xml')
    translator = SBE2Orchestra()
    with open(output_path, 'wb') as f:
        errors = translator.sbe2orch_xml(xml_path, f)
        assert not errors


def test_sbe2orchestra_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples2Orchestra-dict.txt')
    sbe = SBE()
    (sbe_instance, errors) = sbe.read_xml(xml_path)
    translator = SBE2Orchestra()
    orch_instance = translator.sbe2orch_dict(sbe_instance)
    with open(output_path, 'w') as f:
        print(str(orch_instance), file=f)


def test_sbe202orchestra_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples20.xml')
    output_path = os.path.join(output_dir(), 'Examples202Orchestra.xml')
    translator = SBE2Orchestra20_10()
    with open(output_path, 'wb') as f:
        errors = translator.sbe2orch_xml(xml_path, f)
        assert not errors


def test_sbe202orchestra_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples20.xml')
    output_path = os.path.join(output_dir(), 'Examples202Orchestra-dict.txt')
    sbe = SBE20()
    (sbe_instance, errors) = sbe.read_xml(xml_path)
    translator = SBE2Orchestra20_10()
    orch_instance = translator.sbe2orch_dict(sbe_instance)
    with open(output_path, 'w') as f:
        print(str(orch_instance), file=f)
