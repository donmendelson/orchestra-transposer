import logging
from typing import List

from orchestratransposer import UnifiedInstance
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.unified.unified import UnifiedWithPhrases
from orchestratransposer.unified.unifiedinstance import UnifiedInstanceWithPhrases


class Unified2Orchestra10:

    def __init__(self):
        self.logger = logging.getLogger('unified2orchestra')

    def unified2orch_dict(self, unified: UnifiedInstanceWithPhrases, version=None) -> OrchestraInstance10:
        """
        Translate an SBE message schema dictionary to an Orchestra dictionary
        :param unified: a Unified Repository instance
        :param version: a version of fix in Unified Repository to convert. If not provided, it converts the first
        instance found.
        :return: an Orchestra version 1.0 data dictionary
        """
        orch = OrchestraInstance10()
        fix = unified.fix(version)
        self.unified2orch_metadata(fix, orch)
        """datatypes = orch.datatypes()
        self.unified2orch_datatypes(fix, datatypes)
        codesets = orch.codesets()
        self.unified2orch_codesets(fix, codesets)
        fields = orch.fields()
        self.unified2orch_fields(fix, fields)
        self.unified2orch_messages_and_groups(fix, orch)"""
        return orch

    def unified2orch_xml(self, xml_path, phrases_xml_path, stream, version=None) -> List[Exception]:
        unified = UnifiedWithPhrases()
        (unified_instance, errors) = unified.read_xml_all(xml_path, phrases_xml_path)
        self.unified2orch_dict(unified, version)
        return errors

    def unified2orch_metadata(self, fix: dict, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from a Unified Repository
        """
        repository = orch.root()
        repository['@name'] = fix['@version']
        repository['@version'] = fix['@version']


Unified2Orchestra = Unified2Orchestra10
""" Default implementation of Unified Repository to Orchestra conversion """
