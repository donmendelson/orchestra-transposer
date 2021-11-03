import os

from orchestratransposer import SBEOrchestraTransposer, SBE

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path

def test_sbe2orchestra_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples-orch.xml')
    translator = SBEOrchestraTransposer()
    with open(output_path, 'wb') as f:
        errors = translator.sbe2orch_xml(xml_path, f)
        f.close()
        assert not errors


def test_sbe2orchestra_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'Examples.xml')
    output_path = os.path.join(output_dir(), 'Examples-orch-dict.txt')
    sbe = SBE()
    (sbe_instance, errors) = sbe.read_xml(xml_path)
    translator = SBEOrchestraTransposer()
    orch_instance = translator.sbe2orch_dict(sbe_instance)
    with open(output_path, 'w') as f:
        print(str(orch_instance), file=f)
        f.close()