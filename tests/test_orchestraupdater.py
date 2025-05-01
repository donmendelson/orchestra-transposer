import os

from orchestratransposer import Orchestra
from orchestraupdater import Orchestra10_11Updater

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_orchestra10_11_xml():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'Examples10-11.xml')
    updater = Orchestra10_11Updater()
    with open(output_path, 'wb') as f:
        errors = updater.update_xml(xml_path, f)
        assert not errors


def test_orchestra10_11_dict():
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    output_path = os.path.join(output_dir(), 'Examples10-11-dict.txt')
    orchestra = Orchestra()
    (orch_instance, errors) = orchestra.read_xml(xml_path)
    updater = Orchestra10_11Updater()
    orch11_instance = updater.update_dict(orch_instance)
    with open(output_path, 'w') as f:
        print(str(orch11_instance), file=f) 