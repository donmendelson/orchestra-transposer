import os

from orchestratransposer import Unified
from orchestratransposer.unified.unified import UnifiedNoPhrases, UnifiedPhrases

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    unified = UnifiedNoPhrases()
    xml_path = os.path.join(XML_FILE_DIR, 'FixRepository.xml')
    errors = unified.validate(xml_path)
    assert not errors


def test_phrases_valid():
    unified = UnifiedPhrases()
    xml_path = os.path.join(XML_FILE_DIR, 'FIX.Latest_EP269_en_phrases.xml')
    errors = unified.validate(xml_path)
    assert not errors


def test_to_dict():
    unified = UnifiedNoPhrases()
    xml_path = os.path.join(XML_FILE_DIR, 'FixRepository.xml')
    output_path = os.path.join(output_dir(), 'FixRepository-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = unified.read_xml(xml_path)
        print(str(instance), file=f)
        f.close()
        assert not errors


def test_to_from_dict():
    unified = UnifiedNoPhrases()
    xml_path = os.path.join(XML_FILE_DIR, 'FixRepository.xml')
    output_path = os.path.join(output_dir(), 'FixRepository-copy.xml')
    with open(output_path, 'wb') as f:
        (instance, errors) = unified.read_xml(xml_path)
        unified.write_xml(instance, f)
        f.close()
        assert not errors


def test_unified_to_dict():
    unified = Unified()
    xml_path = os.path.join(XML_FILE_DIR, 'FixRepository.xml')
    phrases_xml_path = os.path.join(XML_FILE_DIR, 'FIX.Latest_EP269_en_phrases.xml')
    output_path = os.path.join(output_dir(), 'FixRepository-phrases-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = unified.read_xml(xml_path, phrases_xml_path)
        print(str(instance), file=f)
        f.close()
        assert not errors
