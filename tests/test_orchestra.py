import os
from typing import List, Tuple

from orchestratransposer import Orchestra
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    errors = orchestra.validate(xml_path)
    assert not errors


def test_invalid():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    errors = orchestra.validate(xml_path)
    assert errors


def test_to_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        print(str(instance), file=f)
        assert not errors


def test_invalid_to_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    output_path = os.path.join(output_dir(), 'BadOrchestra-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        print(str(instance), file=f)
        assert errors


def test_to_from_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-copy.xml')
    with open(output_path, 'wb') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        orchestra.write_xml(instance, f)
        assert not errors


def test_documentation():
    code = ['fixr:code',
            {'id': 3547, 'name': 'XMLnonFIX', 'sort': '47', 'value': 'n'},
            ['fixr:annotation',
             ['fixr:documentation', {'purpose': 'SYNOPSIS'}, 'XMLnonFIX'],
             ['fixr:documentation', {'purpose': 'ELABORATION'}]]]
    documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(code)
    assert documentation

