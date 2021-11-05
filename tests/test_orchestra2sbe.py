import os

from orchestratransposer import Orchestra, Orchestra2SBE

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_orchestra2sbe_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-sbe.xml')
    translator = Orchestra2SBE()
    with open(output_path, 'wb') as f:
        errors = translator.orch2sbe_xml(xml_path, f)
        f.close()
        assert not errors


def test_orchestra2sbe_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-sbe-dict.txt')
    orchestra = Orchestra()
    (orch_instance, errors) = orchestra.read_xml(xml_path)
    translator = Orchestra2SBE()
    sbe_instance = translator.orch2sbe_dict(orch_instance)
    with open(output_path, 'w') as f:
        print(str(sbe_instance), file=f)
        f.close()
