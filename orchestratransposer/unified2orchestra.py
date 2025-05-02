import logging
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from orchestra.orchestra import Orchestra10WithAppinfo
from orchestra.orchestrainstance import OrchestraInstance10
from unified.unified import UnifiedWithPhrases
from unified.unifiedinstance import UnifiedInstanceWithPhrases, UnifiedMainInstance


class Unified2Orchestra10:

    def __init__(self):
        self.logger = logging.getLogger('unified2orchestra')

    def unified2orch_dict(self, unified: UnifiedInstanceWithPhrases,
                          version: Optional[str] = None) -> OrchestraInstance10:
        """
        Translate a Unified Repository to an Orchestra dictionary
        :param unified: a Unified Repository instance
        :param version: a version of fix in Unified Repository to convert. If not provided, it converts the first
        instance found.
        :return: an Orchestra version 1.0 data dictionary
        """
        orch = OrchestraInstance10()
        fix = unified.fix(version)
        documentation_func: Callable[[str], List[Tuple[str, List[str]]]] = unified.text_id
        self.unified2orch_metadata(unified, fix, orch)
        sections = orch.sections()
        self.unified2orch_sections(fix, documentation_func, sections)
        categories = orch.categories()
        self.unified2orch_categories(fix, documentation_func, categories)
        datatypes = orch.datatypes()
        self.unified2orch_datatypes(fix, documentation_func, datatypes)
        codesets = orch.codesets()
        self.unified2orch_codesets(fix, documentation_func, codesets)
        fields = orch.fields()
        self.unified2orch_fields(fix, documentation_func, fields)
        components = orch.components()
        self.unified2orch_components(fix, documentation_func, components)
        groups = orch.groups()
        self.unified2orch_groups(fix, documentation_func, groups)
        messages = orch.messages()
        self.unified2orch_messages(fix, documentation_func, messages)
        return orch

    def unified2orch_xml(self, xml_path, phrases_xml_path, orch_stream, version: Optional[str] = None) -> \
            List[Exception]:
        unified = UnifiedWithPhrases()
        (unified_instance, errors) = unified.read_xml_all(xml_path, phrases_xml_path)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orch_instance = self.unified2orch_dict(unified_instance, version)
            orchestra = Orchestra10WithAppinfo()
            errors = orchestra.write_xml(orch_instance, orch_stream)
            if errors:
                for error in errors:
                    self.logger.error(error)
            return errors

    def unified2orch_metadata(self, unified: UnifiedInstanceWithPhrases, fix: list, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from a Unified Repository
        """
        repository = orch.repository()
        version = fix[1]['version']
        (first, sep, last) = version.partition('_')
        repository['version'] = version
        repository['name'] = first
        generated = unified.root()[1]['generated']
        right = unified.root()[1]['copyright']
        metadata = orch.metadata()
        metadata.append(['dcterms:title', version])
        my_date = datetime.now()
        metadata.append(['dcterms:created', my_date.isoformat()])
        metadata.append(['dcterms:date', generated])
        metadata.append(['dcterms:rights', right])
        metadata.append(['dcterms:conformsTo', 'Orchestra v1.0'])
        metadata.append(['dcterms:source', 'FIX Unified Repository 2010 Edition'])

    def unified2orch_sections(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                              sections: list):
        unified_sections = UnifiedMainInstance.sections(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'section', unified_sections)
        for unified_section in lst:
            exclude_keys = {'textId', 'volume', 'id', 'notReqXML'}
            section_attr = {k: unified_section[1][k] for k in set(list(unified_section[1].keys())) - exclude_keys}
            section_attr['name'] = unified_section[1]['id']
            section = ['fixr:section', section_attr]
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(unified_section[1].get('textId',
                                                                                                           None))
            not_req_xml = unified_section[1].get('notReqXML', 0)
            if not_req_xml == 1:
                OrchestraInstance10.append_fixml_appinfo(section, {'notReqXML': 1})
            OrchestraInstance10.append_documentations(section, unified_documentation)
            sections.append(section)

    def unified2orch_categories(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                                categories: list):
        unified_categories = UnifiedMainInstance.categories(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'category', unified_categories)
        for unified_category in lst:
            exclude_keys = ['textId', 'volume', 'id', 'notReqXML', 'generateImplFile']
            category_attr = {k: unified_category[1][k] for k in
                             set(list(unified_category[1].keys())) - set(exclude_keys)}
            category_attr['name'] = unified_category[1]['id']
            category = ['fixr:category', category_attr]
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_category[1].get('textId', None))
            OrchestraInstance10.append_documentations(category, unified_documentation)
            not_req_xml = unified_category[1].get('notReqXML', 0)
            if not_req_xml == 1:
                OrchestraInstance10.append_fixml_appinfo(category, {'notReqXML': 1})
            categories.append(category)

    def unified2orch_datatypes(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                               datatypes: list):
        unified_datatypes = UnifiedMainInstance.datatypes(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'datatype', unified_datatypes)
        for unified_datatype in lst:
            exclude_keys = ['textId', 'builtin', 'issue']
            datatype_attr = {k: unified_datatype[1][k] for k in
                             set(list(unified_datatype[1].keys())) - set(exclude_keys)}
            datatype = ['fixr:datatype', datatype_attr]
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(unified_datatype[1].get('textId',
                                                                                                            None))
            """ TODO annotations with example"""
            unified_xml = next(filter(lambda l: isinstance(l, list) and l[0] == 'XML', unified_datatype), None)
            if unified_xml:
                xml_mapping = ['fixr:mappedDatatype',
                               {k: unified_xml[1][k] for k in set(list(unified_xml[1].keys())) - {'textId'}}]
                xml_mapping[1]['standard'] = 'XML'
                xml_mapping[1]['builtin'] = bool(int(unified_xml[1].get('builtin', '0')))
                unified_xml_documentation: List[Tuple[str, List[str]]] = documentation_func(
                    unified_xml[1].get('textId', None))
                OrchestraInstance10.append_documentations(xml_mapping, unified_xml_documentation)
                datatype.append(xml_mapping)
            OrchestraInstance10.append_documentations(datatype, unified_documentation)
            datatypes.append(datatype)

    def unified2orch_fields(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                            fields: list):
        unified_fields = UnifiedMainInstance.fields(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'field', unified_fields)
        for unified_field in lst:
            exclude_keys = ['textId', 'notReqXML', 'enum', 'associatedDataTag', 'enumDatatype', 'issue']
            field_attr = {k: unified_field[1][k] for k in set(list(unified_field[1].keys())) - set(exclude_keys)}
            field = ['fixr:field', field_attr]
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_field[1].get('textId', None))
            OrchestraInstance10.append_documentations(field, unified_documentation)
            not_req_xml = unified_field[1].get('notReqXML', 0)
            if not_req_xml == 1:
                OrchestraInstance10.append_fixml_appinfo(field, {'notReqXML': 1})
            enum = next(filter(lambda l: isinstance(l, list) and l[0] == 'enum', unified_field), None)
            enum_id = unified_field[1].get('enumDatatype', None)
            if enum_id:
                enum_field = UnifiedMainInstance.field(fix, enum_id)
                if enum_field:
                    codeset_name = enum_field[1]['name'] + 'CodeSet'
                    field_attr['type'] = codeset_name
            elif enum:
                codeset_name = unified_field[1]['name'] + 'CodeSet'
                field_attr['type'] = codeset_name
            else:
                # is this field the associated data field of a Length field? If so, set lengthId.
                unified_length_field = UnifiedMainInstance.field_length_field(fix, unified_field[1]['id'])
                if unified_length_field:
                    field_attr['lengthId'] = unified_length_field[1]['id']
            # does this field have an associated Source field? If so, set discriminatorId.
            unified_source_field = UnifiedMainInstance.discrimintator_field(fix, unified_field[1]['name'])
            if unified_source_field:
                    field_attr['discriminatorId'] = unified_source_field[1]['id']
            fields.append(field)

    def unified2orch_codesets(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                              codesets: list):
        unified_fields = UnifiedMainInstance.fields(fix)
        lst = filter(lambda f: isinstance(f, list) and f[0] == 'field' and len(f) > 2 and f[2][0] == 'enum',
                     unified_fields)
        for unified_field in lst:
            codeset_name = unified_field[1]['name'] + 'CodeSet'
            codeset_attr = {'name': codeset_name, 'id': unified_field[1]['id'], 'type': unified_field[1]['type']}
            codeset = ['fixr:codeSet', codeset_attr]
            d = {k: unified_field[1].get(k, None) for k in
                 ['added', 'addedEP', 'updated', 'updatedEP', 'deprecated',
                  'deprecatedEP']}
            pedigree = dict(filter(lambda item: not item[1] is None, d.items()))
            codeset_attr.update(pedigree)
            enums = filter(lambda e: isinstance(e, list) and e[0] == 'enum', unified_field)
            for idx, enum in enumerate(enums):
                code_attr = {'name': enum[1]['symbolicName'], 'id': unified_field[1]['id'] * 1000 + idx + 1,
                             'value': enum[1]['value']}
                sort = enum[1].get('sort', None)
                if sort:
                    code_attr['sort'] = sort
                group = enum[1].get('group', None)
                if group:
                    code_attr['group'] = group
                d = {k: enum[1].get(k, None) for k in
                     ['added', 'addedEP', 'updated', 'updatedEP', 'deprecated',
                      'deprecatedEP']}
                pedigree = dict(filter(lambda item: not item[1] is None, d.items()))
                code_attr.update(pedigree)
                code = ['fixr:code', code_attr]
                unified_documentation: List[Tuple[str, List[str]]] = documentation_func(enum[1].get('textId', None))
                OrchestraInstance10.append_documentations(code, unified_documentation)
                codeset.append(code)
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_field[1].get('textId', None))
            OrchestraInstance10.append_documentations(codeset, unified_documentation)
            codesets.append(codeset)

    def unified2orch_components(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                                components: list):
        unified_components = UnifiedMainInstance.components(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'component' and l[1].get('repeating', 0) == 0,
                     unified_components)
        for unified_component in lst:
            exclude_keys = ['textId', 'notReqXML', 'type', 'repeating']
            component_attr = {k: unified_component[1][k] for k in
                              set(list(unified_component[1].keys())) - set(exclude_keys)}
            component = ['fixr:component', component_attr]
            self.unified2orch_append_members(fix, documentation_func, component, unified_component)
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(unified_component[1].get('textId',
                                                                                                             None))
            not_req_xml = unified_component[1].get('notReqXML', 0)
            if not_req_xml == 1:
                OrchestraInstance10.append_fixml_appinfo(component, {'notReqXML': 1})
            OrchestraInstance10.append_documentations(component, unified_documentation)
            components.append(component)

    def unified2orch_groups(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                            groups: list):
        unified_components = UnifiedMainInstance.components(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'component' and l[1].get('repeating', 0) == 1,
                     unified_components)
        for unified_component in lst:
            exclude_keys = ['textId', 'notReqXML', 'type', 'repeating']
            group_attr = {k: unified_component[1][k] for k in
                          set(list(unified_component[1].keys())) - set(exclude_keys)}
            group = ['fixr:group', group_attr]
            unified_repeating_group = unified_component[2]
            d = {k: unified_repeating_group[1].get(k, None) for k in
                 ['id', 'added', 'addedEP', 'updated', 'updatedEP', 'deprecated', 'deprecatedEP']}
            num_in_group_attr = dict(filter(lambda item: not item[1] is None, d.items()))
            num_in_group = ['fixr:numInGroup', num_in_group_attr]
            unified_numingroup_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_repeating_group[1].get('textId',
                                               None))
            OrchestraInstance10.append_documentations(num_in_group, unified_numingroup_documentation)
            group.append(num_in_group)
            self.unified2orch_append_members(fix, documentation_func, group, unified_repeating_group)
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_component[1].get('textId', None))
            OrchestraInstance10.append_documentations(group, unified_documentation)
            not_req_xml = unified_component[1].get('notReqXML', 0)
            if not_req_xml == 1:
                OrchestraInstance10.append_fixml_appinfo(group, {'notReqXML': 1})
            groups.append(group)

    def unified2orch_messages(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                              messages: list):
        unified_messages = UnifiedMainInstance.messages(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'message', unified_messages)
        for unified_message in lst:
            exclude_keys = ['textId', 'notReqXML', 'section']
            message_attr = {k: unified_message[1][k] for k in
                            set(list(unified_message[1].keys())) - set(exclude_keys)}
            message = ['fixr:message', message_attr]
            structure = OrchestraInstance10.structure(message)
            self.unified2orch_append_members(fix, documentation_func, structure, unified_message)
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_message[1].get('textId', None))
            OrchestraInstance10.append_documentations(message, unified_documentation)
            not_req_xml = unified_message[1].get('notReqXML', 0)
            if not_req_xml == 1:
                OrchestraInstance10.append_fixml_appinfo(message, {'notReqXML': 1})
            messages.append(message)

    def unified2orch_append_members(self, fix: list, documentation_func: Callable[[str], List[Tuple[str, List[str]]]],
                                    structure: list, unified_structure: list):
        lst = filter(lambda l: isinstance(l, list), unified_structure)
        for unified_member in lst:
            unified_documentation: List[Tuple[str, List[str]]] = documentation_func(
                unified_member[1].get('textId', None))
            presence = Unified2Orchestra10.unified2orch_presence(unified_member[1].get('required', 0))
            if unified_member[0] == 'fieldRef':
                exclude_keys = ['textId', 'inlined', 'legacyIndent', 'legacyPosition', 'name', 'required', 'issue']
                field_attr = {k: unified_member[1][k] for k in
                              set(list(unified_member[1].keys())) - set(exclude_keys)}
                if not presence == 'optional':
                    field_attr['presence'] = presence
                field_ref = ['fixr:fieldRef', field_attr]
                OrchestraInstance10.append_documentations(field_ref, unified_documentation)
                structure.append(field_ref)
            elif unified_member[0] == 'componentRef':
                component_id = unified_member[1]['id']
                component = UnifiedMainInstance.component(fix, component_id)
                if component[1].get('repeating', 0) == 1:
                    exclude_keys = ['textId', 'inlined', 'legacyIndent', 'legacyPosition', 'name', 'required', 'issue']
                    group_attr = {k: unified_member[1][k] for k in
                                  set(list(unified_member[1].keys())) - set(exclude_keys)}
                    if not presence == 'optional':
                        group_attr['presence'] = presence
                    group_ref = ['fixr:groupRef', group_attr]
                    OrchestraInstance10.append_documentations(group_ref, unified_documentation)
                    structure.append(group_ref)
                else:
                    exclude_keys = ['textId', 'inlined', 'legacyIndent', 'legacyPosition', 'name', 'required', 'issue']
                    component_attr = {k: unified_member[1][k] for k in
                                      set(list(unified_member[1].keys())) - set(exclude_keys)}
                    if not presence == 'optional':
                        component_attr['presence'] = presence
                    component_ref = ['fixr:componentRef', component_attr]
                    inlined = unified_member[1].get('inlined', 0)
                    if inlined == 1:
                        OrchestraInstance10.append_fixml_appinfo(component_ref, {'inlined': 1})
                    OrchestraInstance10.append_documentations(component_ref, unified_documentation)
                    structure.append(component_ref)

    @staticmethod
    def unified2orch_presence(unified_required: int) -> str:
        """ Translate Unified required to Orchestra presence string """
        if unified_required == 1:
            return 'required'
        else:
            return 'optional'


Unified2Orchestra = Unified2Orchestra10
""" Default implementation of Unified Repository to Orchestra conversion """
