import os

import pytest
from pysbeorchestra import SBE, Orchestra, OrchestraInstance, SBEInstance, SBEOrchestraTranslator

XML_FILE_DIR = os.path.join(os.path.dirname(__file__), 'xml/')


def output_dir():
    path = os.path.join(os.path.dirname(__file__), 'out/')
    os.makedirs(path, exist_ok=True)
    return path

def test_orchestra2sbe():
    output_path = os.path.join(output_dir(), 'OrchestraFIXLatest-sbe.xml')
    xml_path = os.path.join(XML_FILE_DIR, 'OrchestraFIXLatest.xml')
    translator = SBEOrchestraTranslator()
    with open(output_path, 'wb') as f:
        errors = translator.orchestra2sbe(xml_path, f)
        f.close
        assert not errors
