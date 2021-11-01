import os

from orchestratransposer import Orchestra

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path


def test_valid():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    error_iter = orchestra.validate(xml_path)
    assert not next(error_iter, None)


def test_invalid():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    error_iter = orchestra.validate(xml_path)
    assert next(error_iter, None)


def test_to_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatestSBE-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        print(instance, file=f)
        f.close()
        assert not errors


def test_invalid_to_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'BadOrchestra.xml')
    output_path = os.path.join(output_dir(), 'BadOrchestra-dict.txt')
    with open(output_path, 'w') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        print(instance, file=f)
        f.close()
        assert errors


def test_to_from_dict():
    orchestra = Orchestra()
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatestWithSBE.xml')
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatestWithSBE-copy.xml')
    with open(output_path, 'wb') as f:
        (instance, errors) = orchestra.read_xml(xml_path)
        orchestra.write_xml(instance, f)
        f.close()
        assert not errors
