import logging
from datetime import datetime
from typing import Callable, List, Tuple

from orchestra.orchestra import Orchestra10WithAppinfo
from orchestra.orchestrainstance import OrchestraInstance10
from unified.unified import UnifiedWithPhrases
from unified.unifiedinstance import UnifiedInstanceWithPhrases, UnifiedMainInstance


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
        orchestra = Orchestra10WithAppinfo()
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
        rights = orch.metadata_term('dcterms:rights')
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
            if appinfo and appinfo[0][1].get('notReqXML', 0) == '1':
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
            if appinfo and appinfo[0][1].get('notReqXML', 0) == '1':
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
            codeset = orch.codeset_by_name(field_type)
            unified_field_attr = {k: field[1][k] for k in
                                  set(list(field[1].keys())) - {'lengthId', 'discriminatorId'}}
            appinfo = OrchestraInstance10.appinfo(field, 'FIXML')
            if appinfo and appinfo[0][1].get('notReqXML', 0) == '1':
                unified_field_attr['notReqXML'] = 1
            unified_field = ['field', unified_field_attr]
            if codeset:
                unified_field_attr['type'] = codeset[1]['type']
                if field[1]['id'] == codeset[1]['id']:
                    code_lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:code', codeset)
                    for code in code_lst:
                        enum_attr = {k: code[1][k] for k in
                                     set(list(code[1].keys())) - {'name', 'id'}}
                        enum_attr['symbolicName'] = code[1]['name']
                        enum = ['enum', enum_attr]
                        documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(code)
                        if len(documentation):
                            text_id = 'ENUM_' + str(field[1]['id']) + '_' + str(code[1]['value'])
                            enum_attr['textId'] = text_id
                            documentation_func(text_id, documentation)
                        unified_field.append(enum)
                else:
                    # Deduplicate enums
                    unified_field_attr['enumDatatype'] = codeset[1]['id']
            else:
                # is this field the length field of a data field? If so, set associatedDataTag.
                orch_data_field = orch.field_data_field(field[1]['id'])
                if orch_data_field:
                    unified_field_attr['associatedDataTag'] = orch_data_field[1]['id']
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
            if component[1]['name'] in ['SecurityXML', 'DerivativeSecurityXML', 'LegSecurityXML',
                                        'UnderlyingSecurityXML']:
                unified_component_attr['type'] = 'XMLDataBlock'
            else:
                unified_component_attr['type'] = 'Block'
            unified_component_attr['repeating'] = 0
            appinfo = OrchestraInstance10.appinfo(component, 'FIXML')
            if appinfo and appinfo[0][1].get('notReqXML', 0) == '1':
                unified_component_attr['notReqXML'] = 1
            unified_component = ['component', unified_component_attr]
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(component)
            if documentation:
                text_id = 'COMP_' + component[1]['name'] + '_TITLE'
                unified_component_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_components.append(unified_component)
            self.orch2unified_append_members(orch, component, documentation_func,
                                             'CMP_' + str(unified_component_attr['id']),
                                             unified_component)

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
            if appinfo and appinfo[0][1].get('notReqXML', 0) == '1':
                unified_component_attr['notReqXML'] = 1
            unified_component = ['component', unified_component_attr]
            # repeatingGroup attributes derived from Orchestra numInGroup attributes
            repeating_attr = {k: group[2][1][k] for k in set(list(group[2][1].keys())) - {'presence'}}
            repeating_attr['name'] = ""
            repeating_attr['legacyPosition'] = 0
            repeating_attr['legacyIndent'] = 0
            repeating_attr['required'] = 1 if group[2][1].get("presence", "") == 'required' else 0
            repeating_group = ['repeatingGroup', repeating_attr]
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(group[2])
            if documentation:
                text_id = 'CMP_' + str(unified_component_attr['id']) + 'REF_' + str(repeating_attr['id'])
                repeating_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_component.append(repeating_group)
            group_documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(group)
            if group_documentation:
                text_id = 'COMP_' + group[1]['name'] + '_TITLE'
                unified_component_attr['textId'] = text_id
                documentation_func(text_id, group_documentation)
            unified_components.append(unified_component)
            self.orch2unified_append_members(orch, group, documentation_func,
                                             'CMP_' + str(unified_component_attr['id']),
                                             repeating_group)

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
            if appinfo and appinfo[0][1].get('notReqXML', 0) == '1':
                unified_message_attr['notReqXML'] = 1
            else:
                unified_message_attr['notReqXML'] = 0
            structure = message[2]
            unified_message = ['message', unified_message_attr]
            documentation: List[Tuple[str, str]] = OrchestraInstance10.documentation(message)
            if documentation:
                text_id = 'MSG_' + str(message[1]['id']) + '_TITLE'
                unified_message_attr['textId'] = text_id
                documentation_func(text_id, documentation)
            unified_messages.append(unified_message)
            self.orch2unified_append_members(orch, structure, documentation_func,
                                             'MSG_' + str(unified_message_attr['id']),
                                             unified_message)

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
                if appinfo and appinfo[0][1].get('inlined', 0) == '1':
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
