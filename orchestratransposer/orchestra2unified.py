import logging
from datetime import datetime
from typing import Callable, List, Tuple

from orchestratransposer.orchestra.orchestra import Orchestra10
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.unified.unified import UnifiedWithPhrases
from orchestratransposer.unified.unifiedinstance import UnifiedInstanceWithPhrases, UnifiedMainInstance


class Orchestra10Unified:

    def __init__(self):
        self.logger = logging.getLogger('orchestra2unified')

    def orch2unified_dict(self, orchestra: OrchestraInstance10) -> UnifiedInstanceWithPhrases:
        unified = UnifiedInstanceWithPhrases()
        documentation_func: Callable[[str, List[Tuple[str, str]]], None] = unified.append_documentation
        fix: list = self.orch2unified_metadata(orchestra, unified)
        self.orch2unified_datatypes(orchestra, documentation_func, fix)
        self.orch2unified_categories(orchestra, documentation_func, fix)
        self.orch2unified_sections(orchestra, documentation_func, fix)
        self.orch2unified_fields(orchestra, documentation_func, fix)
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
            return unified.write_xml_all(unified_instance, unified_stream, phrases_stream)

    def orch2unified_metadata(self, orch: OrchestraInstance10, unified: UnifiedInstanceWithPhrases) -> list:
        """
        Set Unified metadata from Orchestra, returns instance of fix
        """
        repository = orch.repository()
        generated = datetime.now().isoformat()
        unified.root()[1]['generated'] = generated
        rights = orch.metadata_term('dc:rights')
        if rights:
            unified.root()[1]['copyright'] = rights
        unified.phrases.phrases_root()[1]['generated'] = generated
        unified.phrases.phrases_root()[1]['langId'] = 'en'
        version = repository['version']
        unified.phrases.phrases_root()[1]['version'] = version
        return unified.fix(version)

    def orch2unified_sections(self, orch: OrchestraInstance10,
                              documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                              fix: list):
        unified_sections = UnifiedMainInstance.sections(fix)
        sections: list = orch.sections()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:section', sections)
        for section in lst:
            section_attr = section[1]
            section_attr['id'] = section[1]['name']
            unified_section = ['section', section_attr]
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(section)
            if documentation:
                text_id = 'SCT_' + section[1]['name']
                section_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_sections.append(unified_section)

    def orch2unified_categories(self, orch: OrchestraInstance10,
                                documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                                fix: list):
        unified_categories = UnifiedMainInstance.categories(fix)
        categories: list = orch.categories()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:category', categories)
        for category in lst:
            category_attr = {k: category[1][k] for k in set(list(category[1].keys())) - set(['name'])}
            category_attr['id'] = category[1]['name']
            unified_category = ['category', category_attr]
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(category)
            if documentation:
                text_id = 'CAT_' + category[1]['name']
                category_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_categories.append(unified_category)

    def orch2unified_datatypes(self, orch: OrchestraInstance10,
                               documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                               fix: list):
        unified_datatypes: list = UnifiedMainInstance.datatypes(fix)
        datatypes: list = orch.datatypes()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:datatype', datatypes)
        for datatype in lst:
            datatype_attr = datatype[1]
            unified_datatype = ['datatype', datatype_attr]
            xml = next(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:mappedDatatype', datatype), None)
            if xml:
                unified_xml_mapping = ['XML',
                                       {k: xml[1][k] for k in
                                        set(list(xml[1].keys())) - set(['standard', 'builtin'])}]
                unified_xml_mapping[1]['builtin'] = '1' if xml[1].get('builtin', False) else '0'
                documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(xml)
                if documentation:
                    text_id = 'DT_XML_' + datatype[1]['name']
                    unified_xml_mapping[1]['textId'] = text_id
                    documentation_func(text_id, documentation)
                unified_datatype.append(unified_xml_mapping)
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(datatype)
            if documentation:
                text_id = 'DT_' + datatype[1]['name']
                datatype_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_datatypes.append(unified_datatype)

    def orch2unified_fields(self, orch: OrchestraInstance10,
                           documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                           fix: list):
        unified_fields = UnifiedMainInstance.fields(fix)
        fields: list = orch.fields()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:field', fields)
        for field in lst:
            field_type = field[1]['type']
            codeset = orch.codeset(field_type)
            field_attr = {k: field[1][k] for k in
                          set(list(field[1].keys())) - set(['lengthId', 'discriminatorId'])}
            unified_field = ['field', field_attr]
            if codeset:
                field_attr['type'] = codeset[1]['type']
                code_lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:code', codeset)
                for code in code_lst:
                    enum_attr = {k: code[1][k] for k in
                                 set(list(code[1].keys())) - set(['name', 'id'])}
                    enum_attr['symbolicName'] = code[1]['name']
                    enum = ['enum', enum_attr]
                    documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(code)
                    if documentation:
                        text_id = 'ENUM_' + str(field[1]['id']) + '_' + str(code[1]['value'])
                        enum_attr['textId'] = text_id
                        documentation_func(text_id, documentation)
                    unified_field.append(enum)
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(field)
            if documentation:
                text_id = 'FIELD_' + str(field[1]['id'])
                field_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_fields.append(unified_field)


Orchestra2Unified = Orchestra10Unified
""" Default implementation of Orchestra to Unified Repository conversion """
