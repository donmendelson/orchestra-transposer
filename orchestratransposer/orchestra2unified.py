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
        self.orch2unified_components(orchestra, documentation_func, fix)
        self.orch2unified_groups(orchestra, documentation_func, fix)
        self.orch2unified_messages(orchestra, documentation_func, fix)
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
            errors = unified.write_xml_all(unified_instance, unified_stream, phrases_stream)
            for error in errors:
                self.logger.error(error)
            return errors

    def orch2unified_metadata(self, orch: OrchestraInstance10, unified: UnifiedInstanceWithPhrases) -> list:
        """
        Set Unified metadata from Orchestra, returns instance of fix
        """
        repository = orch.repository()
        generated = datetime.now().isoformat()
        unified.root()[1]['generated'] = generated
        rights = orch.metadata_term('dc:rights')
        if not rights:
            rights = 'Rights unknown'  # not the same as no copyright
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
            unified_section_attr = section[1].copy()
            unified_section_attr['id'] = section[1]['name']
            unified_section = ['section', unified_section_attr]
            appinfo = OrchestraInstance10.appinfo(section, 'FIXML')
            if 'notReqXML' in appinfo:
                unified_section_attr['notReqXML'] = 1
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(section)
            if documentation:
                text_id = 'SCT_' + section[1]['name']
                unified_section_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_sections.append(unified_section)

    def orch2unified_categories(self, orch: OrchestraInstance10,
                                documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                                fix: list):
        unified_categories = UnifiedMainInstance.categories(fix)
        categories: list = orch.categories()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:category', categories)
        for category in lst:
            unified_category_attr = {k: category[1][k] for k in set(list(category[1].keys())) - {'name'}}
            unified_category_attr['id'] = category[1]['name']
            unified_category = ['category', unified_category_attr]
            appinfo = OrchestraInstance10.appinfo(category, 'FIXML')
            if 'notReqXML' in appinfo:
                unified_category_attr['notReqXML'] = 1
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(category)
            if documentation:
                text_id = 'CAT_' + category[1]['name']
                unified_category_attr['textId'] = text_id
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
                                        set(list(xml[1].keys())) - {'standard', 'builtin'}}]
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
            unified_field_attr = {k: field[1][k] for k in
                                  set(list(field[1].keys())) - {'lengthId', 'discriminatorId'}}
            appinfo = OrchestraInstance10.appinfo(field, 'FIXML')
            if 'notReqXML' in appinfo:
                unified_field_attr['notReqXML'] = 1
            unified_field = ['field', unified_field_attr]
            if codeset:
                # Deduplicate enums
                if field[1]['id'] == codeset[1]['id']:
                    unified_field_attr['type'] = codeset[1]['type']
                    code_lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:code', codeset)
                    for code in code_lst:
                        enum_attr = {k: code[1][k] for k in
                                     set(list(code[1].keys())) - {'name', 'id'}}
                        enum_attr['symbolicName'] = code[1]['name']
                        enum = ['enum', enum_attr]
                        documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(code)
                        if documentation:
                            text_id = 'ENUM_' + str(field[1]['id']) + '_' + str(code[1]['value'])
                            enum_attr['textId'] = text_id
                            documentation_func(text_id, documentation)
                        unified_field.append(enum)
                else:
                    unified_field_attr['enumDatatype'] = codeset[1]['id']
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(field)
            if documentation:
                text_id = 'FIELD_' + str(field[1]['id'])
                unified_field_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_fields.append(unified_field)

    def orch2unified_components(self, orch: OrchestraInstance10,
                                documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                                fix: list):
        unified_components = UnifiedMainInstance.components(fix)
        components: list = orch.components()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:component', components)
        for component in lst:
            unified_component_attr = component[1].copy()
            unified_component_attr['type'] = 'Block'
            unified_component_attr['repeating'] = 0
            appinfo = OrchestraInstance10.appinfo(component, 'FIXML')
            if 'notReqXML' in appinfo:
                unified_component_attr['notReqXML'] = 1
            unified_component = ['component', unified_component_attr]
            self.orch2unified_append_members(orch, component, documentation_func,
                                             'CMP_' + str(unified_component_attr['id']),
                                             unified_component)
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(component)
            if documentation:
                text_id = 'COMP_' + component[1]['name'] + '_TITLE'
                unified_component_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_components.append(unified_component)

    def orch2unified_groups(self, orch: OrchestraInstance10,
                            documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                            fix: list):
        unified_components = UnifiedMainInstance.components(fix)
        groups: list = orch.groups()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:group', groups)
        for group in lst:
            unified_component_attr = group[1].copy()
            unified_component_attr['type'] = 'BlockRepeating'
            unified_component_attr['repeating'] = 1
            appinfo = OrchestraInstance10.appinfo(group, 'FIXML')
            if 'notReqXML' in appinfo:
                unified_component_attr['notReqXML'] = 1
            unified_component = ['component', unified_component_attr]
            repeating_attr = {'legacyIndent': 0,
                              'legacyPosition': 0,
                              'name': '',
                              'required': 0}
            repeating_group = ['repeatingGroup', repeating_attr]
            unified_component.append(repeating_group)
            self.orch2unified_append_members(orch, group, documentation_func,
                                             'CMP_' + str(unified_component_attr['id']),
                                             repeating_group)
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(group)
            if documentation:
                text_id = 'COMP_' + group[1]['name'] + '_TITLE'
                unified_component_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_components.append(unified_component)

    def orch2unified_messages(self, orch: OrchestraInstance10,
                              documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                              fix: list):
        unified_messages = UnifiedMainInstance.messages(fix)
        messages: list = orch.messages()
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:message', messages)
        for message in lst:
            unified_message_attr = message[1].copy()
            category = orch.category(message[1]['category'])
            if category:
                section = category[1]['section']
                unified_message_attr['section'] = section
            else:
                unified_message_attr['section'] = 'Unknown'
                self.logger.error("Section not found for message %d", unified_message_attr['id'])
            appinfo = OrchestraInstance10.appinfo(message, 'FIXML')
            unified_message_attr['notReqXML'] = 1 if 'notReqXML' in appinfo else 0
            structure = message[2]
            unified_message = ['message', unified_message_attr]
            self.orch2unified_append_members(orch, structure, documentation_func,
                                             'MSG_' + str(unified_message_attr['id']),
                                             unified_message)
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(message)
            if documentation:
                text_id = 'MSG_' + str(message[1]['id']) + '_TITLE'
                unified_message_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_messages.append(unified_message)

    def orch2unified_append_members(self, orch: OrchestraInstance10, structure: list,
                                    documentation_func: Callable[[str, List[Tuple[str, str]]], None],
                                    prefix: str,
                                    unified_structure: list):
        lst = filter(lambda l: isinstance(l, list) and l[0] in ['fixr:fieldRef', 'fixr:componentRef', 'fixr:groupRef',
                                                                'fixr:numInGroup'],
                     structure)
        for member in lst:
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(member)
            unified_presence = Orchestra10Unified.orch2unified_presence(member[1].get('presence', 'optional'))
            member_id = member[1]['id']
            if member[0] == 'fixr:numInGroup':
                field_attr = member[1]
                # update parent repeatinggroup element
                unified_structure[1]['id'] = field_attr['id']
                if documentation:
                    text_id = prefix + '_REF_' + str(member_id)
                    unified_structure[1]['textId'] = text_id
                    documentation_func(text_id, documentation)
            elif member[0] == 'fixr:fieldRef':
                field = orch.field(member_id)
                unified_field_attr = {k: member[1][k] for k in
                                      set(list(member[1].keys())) - {'presence'}}
                unified_field_attr['required'] = unified_presence
                unified_field_attr['legacyPosition'] = 0
                unified_field_attr['legacyIndent'] = 0
                if field:
                    unified_field_attr['name'] = field[1]['name']
                else:
                    unified_field_attr['name'] = 'Unknown'
                    self.logger.error("Field %d not found", member_id)
                unified_field_ref = ['fieldRef', unified_field_attr]
                if documentation:
                    text_id = prefix + '_REF_' + str(member_id)
                    unified_field_attr['textId'] = text_id
                    documentation_func(text_id, documentation)
                unified_structure.append(unified_field_ref)
            elif member[0] == 'fixr:componentRef':
                component = orch.component(member_id)
                unified_component_attr = {k: member[1][k] for k in
                                          set(list(member[1].keys())) - {'presence'}}
                unified_component_attr['required'] = unified_presence
                unified_component_attr['legacyPosition'] = 0
                unified_component_attr['legacyIndent'] = 0
                appinfo = OrchestraInstance10.appinfo(member, 'FIXML')
                if 'inlined' in appinfo:
                    unified_component_attr['inlined'] = True
                unified_component_ref = ['componentRef', unified_component_attr]
                if component:
                    unified_component_attr['name'] = component[1]['name']
                    if documentation:
                        text_id = prefix + '_REF_' + component[1]['name']
                        unified_component_attr['textId'] = text_id
                        documentation_func(text_id, documentation)
                else:
                    unified_component_attr['name'] = 'Unknown'
                    self.logger.error("Component %d not found", member_id)
                unified_structure.append(unified_component_ref)
            elif member[0] == 'fixr:groupRef':
                group = orch.group(member_id)
                unified_component_attr = {k: member[1][k] for k in
                                          set(list(member[1].keys())) - {'presence'}}

                unified_component_attr['required'] = unified_presence
                unified_component_attr['legacyPosition'] = 0
                unified_component_attr['legacyIndent'] = 0
                unified_component_ref = ['componentRef', unified_component_attr]
                if group:
                    unified_component_attr['name'] = group[1]['name']
                    if documentation:
                        text_id = prefix + '_REF_' + group[1]['name']
                        unified_component_attr['textId'] = text_id
                        documentation_func(text_id, documentation)
                else:
                    unified_component_attr['name'] = 'Unknown'
                    self.logger.error("Group %d not found", member_id)
                unified_structure.append(unified_component_ref)

    @staticmethod
    def orch2unified_presence(presence: str):
        return 1 if presence == 'required' else 0


Orchestra2Unified = Orchestra10Unified
""" Default implementation of Orchestra to Unified Repository conversion """
