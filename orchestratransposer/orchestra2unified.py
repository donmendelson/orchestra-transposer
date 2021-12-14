import logging
from datetime import datetime
from typing import List, Tuple

from orchestratransposer.orchestra.orchestra import Orchestra10
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.unified.unified import UnifiedWithPhrases
from orchestratransposer.unified.unifiedinstance import UnifiedInstanceWithPhrases, UnifiedMainInstance


class Orchestra10Unified:

    def __init__(self):
        self.logger = logging.getLogger('orchestra2unified')

    def orch2unified_dict(self, orchestra: OrchestraInstance10) -> UnifiedInstanceWithPhrases:
        unified = UnifiedInstanceWithPhrases()
        fix: list = self.orch2unified_metadata(orchestra, unified)
        self.orch2unified_sections(orchestra, unified, fix)
        # self.orch2unified_categories(orchestra, fix)
        # self.orch2unified_datatypes(orchestra, fix)
        # self.orch2unified_codesets(orchestra, fix)
        # self.orch2unified_field(orchestra, fix)
        # self.orch2unified_components(orchestra, fix)
        # self.orch2unified_groups(orchestra, fix)
        # self.orch2unified_messages(orchestra, fix)
        return unified

    def orch2unified_xml(self, orchestra_xml, unified_stream, phrases_stream) -> List[Exception]:
        orchestra = Orchestra10()
        (orch_instance, errors) = orchestra.read_xml(orchestra_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            unified_instance = self.orch2unified_dict(orch_instance)
            unified = UnifiedWithPhrases()
            unified.write_xml_all(unified_instance, unified_stream, phrases_stream)

    def orch2unified_metadata(self, orch: OrchestraInstance10, unified: UnifiedInstanceWithPhrases) -> list:
        """
        Set Unified metadata from Orchestra, returns instance of fix
        """
        repository = orch.repository()
        version = repository['version']
        return unified.fix(version)

    def orch2unified_sections(self, orch: OrchestraInstance10, unified: UnifiedInstanceWithPhrases, fix: list):
        unified_sections = UnifiedMainInstance.sections(fix)
        sections: list = orch.sections()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:section', sections)
        for section in lst:
            section_attr = section[1]
            text_id = 'SCT_' + section[1]['name']
            section_attr['textId'] = text_id
            unified_section = ['section', section_attr]
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(section)
            unified.append_documentation(text_id, documentation)
            unified_sections.append(unified_section)


Orchestra2Unified = Orchestra10Unified
""" Default implementation of Orchestra to Unified Repository conversion """
