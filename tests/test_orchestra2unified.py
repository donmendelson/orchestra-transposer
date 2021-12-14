import os

from orchestratransposer import Orchestra, Orchestra2Unified, Unified2Orchestra, Unified

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_orchestra2unified_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    phrases_xml_path = os.path.join(output_dir(), 'OrchestraFIXLatest_en_phrases.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest2Unified.xml')
    translator = Orchestra2Unified()
    with open(output_path, 'wb') as unified_stream, open(phrases_xml_path, 'wb') as phrases_stream:
        errors = translator.orch2unified_xml(xml_path, unified_stream, phrases_stream)
        unified_stream.close()
        phrases_stream.close()
        assert not errors


def test_orchestra2unified_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    phrases_xml_path = os.path.join(XML_FILE_DIR, 'FIX.Latest_EP269_en_phrases.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest2Unified-dict.txt')
    orchestra = Orchestra()
    (orchestra_instance, errors) = orchestra.read_xml(xml_path)
    assert not errors
    translator = Orchestra2Unified()
    unified_instance = translator.orch2unified_dict(orchestra_instance)
    with open(output_path, 'w') as f:
        print(str(unified_instance), file=f)
        f.close()
