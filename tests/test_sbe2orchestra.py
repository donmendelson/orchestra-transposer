import os

from pysbeorchestra import SBE, Orchestra, SBEOrchestraTranslator

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_orchestra2sbe_xml():
    sbe = SBE()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-sbe-dict.txt')
    translator = SBEOrchestraTranslator()
    with open(output_path, 'wb') as f:
        errors = translator.orchestra2sbe_xml(xml_path, f)
        f.close
        assert not errors


def test_orchestra2sbe_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-sbe-dict.txt')
    orchestra = Orchestra()
    (orch_instance, errors) = orchestra.read_xml(xml_path)
    translator = SBEOrchestraTranslator()
    sbe_instance = translator.orchestra_2sbe_dict(orch_instance)
    with open(output_path, 'w') as f:
        print(str(sbe_instance), file=f)
        f.close
