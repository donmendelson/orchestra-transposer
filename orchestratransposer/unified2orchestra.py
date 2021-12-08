import logging
from datetime import datetime
from typing import List, Optional

from orchestratransposer.orchestra.orchestra import Orchestra10
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.unified.unified import UnifiedWithPhrases
from orchestratransposer.unified.unifiedinstance import UnifiedInstanceWithPhrases, UnifiedMainInstance


class Unified2Orchestra10:

    def __init__(self):
        self.logger = logging.getLogger('unified2orchestra')

    def unified2orch_dict(self, unified: UnifiedInstanceWithPhrases,
                          version: Optional[str] = None) -> OrchestraInstance10:
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
        sections = orch.sections()
        self.unified2orch_sections(fix, sections)
        categories = orch.categories()
        self.unified2orch_categories(fix, categories)
        datatypes = orch.datatypes()
        self.unified2orch_datatypes(fix, datatypes)
        codesets = orch.codesets()
        self.unified2orch_codesets(fix, codesets)
        fields = orch.fields()
        self.unified2orch_fields(fix, fields)
        components = orch.components()
        self.unified2orch_components(fix, components)
        groups = orch.groups()
        self.unified2orch_groups(fix, groups)
        messages = orch.messages()
        self.unified2orch_messages(fix, messages)
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
            orchestra = Orchestra10()
            errors = orchestra.write_xml(orch_instance, orch_stream)
            if errors:
                for error in errors:
                    self.logger.error(error)
            return errors

    def unified2orch_metadata(self, fix: list, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from a Unified Repository
        """
        repository = orch.repository()
        version = fix[1]['version']
        (first, sep, last) = version.partition('_')
        repository['version'] = version
        repository['name'] = first
        metadata = orch.metadata()
        metadata.append(['dcterms:title', first])
        my_date = datetime.now()
        metadata.append(['dcterms:date', my_date.isoformat()])

    def unified2orch_sections(self, fix: list, sections: list):
        unified_sections = UnifiedMainInstance.sections(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'section', unified_sections)
        for unified_section in lst:
            exclude_keys = ['textId', 'volume', 'id', 'notReqXML']
            section_attr = {k: unified_section[1][k] for k in set(list(unified_section[1].keys())) - set(exclude_keys)}
            section_attr['name'] = unified_section[1]['id']
            section = ['fixr:section', section_attr]
            sections.append(section)

    def unified2orch_categories(self, fix: list, categories: list):
        unified_categories = UnifiedMainInstance.categories(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'category', unified_categories)
        for unified_category in lst:
            exclude_keys = ['textId', 'volume', 'id', 'notReqXML', 'generateImplFile']
            category_attr = {k: unified_category[1][k] for k in
                             set(list(unified_category[1].keys())) - set(exclude_keys)}
            category_attr['name'] = unified_category[1]['id']
            category = ['fixr:category', category_attr]
            categories.append(category)

    def unified2orch_datatypes(self, fix: list, datatypes: list):
        unified_datatypes = UnifiedMainInstance.datatypes(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'datatype', unified_datatypes)
        for unified_datatype in lst:
            exclude_keys = ['textId', 'builtin']
            datatype_attr = {k: unified_datatype[1][k] for k in
                             set(list(unified_datatype[1].keys())) - set(exclude_keys)}
            datatype = ['fixr:datatype', datatype_attr]
            """ TODO annotations with example"""
            xml = next(filter(lambda l: isinstance(l, list) and l[0] == 'XML', unified_datatype), None)
            if xml:
                xml_mapping = ['fixr:mappedDatatype',
                               {k: xml[1][k] for k in set(list(xml[1].keys())) - set(exclude_keys)}]
                xml_mapping[1]['standard'] = 'XML'
                xml_mapping[1]['builtin'] = bool(int(xml[1].get('builtin', '0')))
                datatype.append(xml_mapping)
            datatypes.append(datatype)

    def unified2orch_fields(self, fix: list, fields: list):
        unified_fields = UnifiedMainInstance.fields(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'field', unified_fields)
        for unified_field in lst:
            exclude_keys = ['textId', 'notReqXML', 'enum', 'associatedDataTag', 'enumDatatype']
            field_attr = {k: unified_field[1][k] for k in set(list(unified_field[1].keys())) - set(exclude_keys)}
            field = ['fixr:field', field_attr]
            enum = next(filter(lambda l: isinstance(l, list) and l[0] == 'enum', unified_field), None)
            if enum:
                codeset_name = unified_field[1]['name']
                enum_id = unified_field[1].get('enumDatatype', None)
                if enum_id:
                    enum_field = UnifiedMainInstance.field(fix, enum_id)
                    if enum_field:
                        codeset_name = enum_field[1]['name']
                field_attr['type'] = codeset_name + 'CodeSet'
            assoc_id = unified_field[1].get('associatedDataTag', None)
            if assoc_id:
                assoc_field = UnifiedMainInstance.field(fix, assoc_id)
                if assoc_field:
                    field_attr['lengthId'] = assoc_field[1]['id']
            fields.append(field)

    def unified2orch_codesets(self, fix: list, codesets: list):
        unified_fields = UnifiedMainInstance.fields(fix)
        lst = filter(lambda f: isinstance(f, list) and f[0] == 'field' and len(f) > 2 and f[2][0] == 'enum',
                     unified_fields)
        for unified_field in lst:
            codeset_name = unified_field[1]['name'] + 'CodeSet'
            codeset_attr = {'name': codeset_name, 'id': unified_field[1]['id'], 'type': unified_field[1]['type']}
            codeset = ['fixr:codeSet', codeset_attr]
            d = {k: unified_field[1].get(k, None) for k in
                 ['added', 'addedEP', 'updated, updatedEP', 'deprecated',
                  'deprecatedEP']}
            pedigree = dict(filter(lambda item: not item[1] is None, d.items()))
            codeset_attr.update(pedigree)
            enums = filter(lambda e: isinstance(e, list) and e[0] == 'enum', unified_field)
            for idx, enum in enumerate(enums):
                code_attr = {'name': enum[1]['symbolicName'], 'id': unified_field[1]['id'] * 100 + idx + 1,
                             'value': enum[1]['value']}
                code = ['fixr:code', code_attr]
                codeset.append(code)
            codesets.append(codeset)

    def unified2orch_components(self, fix: list, components: list):
        unified_components = UnifiedMainInstance.components(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'component' and l[1].get('repeating', 0) == 0,
                     unified_components)
        for unified_component in lst:
            exclude_keys = ['textId', 'notReqXML', 'type', 'repeating']
            component_attr = {k: unified_component[1][k] for k in
                              set(list(unified_component[1].keys())) - set(exclude_keys)}
            component = ['fixr:component', component_attr]
            self.unified2orch_components_append_members(fix, component, unified_component)
            components.append(component)

    def unified2orch_groups(self, fix: list, groups: list):
        unified_components = UnifiedMainInstance.components(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'component' and l[1].get('repeating', 0) == 1,
                     unified_components)
        for unified_component in lst:
            exclude_keys = ['textId', 'notReqXML', 'type', 'repeating']
            group_attr = {k: unified_component[1][k] for k in
                          set(list(unified_component[1].keys())) - set(exclude_keys)}
            group = ['fixr:group', group_attr]
            unified_repeating_group = unified_component[2]
            self.unified2orch_components_append_members(fix, group, unified_repeating_group)
            groups.append(group)

    def unified2orch_messages(self, fix: list, messages: list):
        unified_messages = UnifiedMainInstance.messages(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'message', unified_messages)
        for unified_message in lst:
            exclude_keys = ['textId', 'notReqXML', 'section']
            message_attr = {k: unified_message[1][k] for k in
                            set(list(unified_message[1].keys())) - set(exclude_keys)}
            message = ['fixr:message', message_attr]
            structure = OrchestraInstance10.structure(message)
            self.unified2orch_components_append_members(fix, structure, unified_message)
            messages.append(message)

    def unified2orch_components_append_members(self, fix: list, structure: list, unified_structure: list):
        lst = filter(lambda l: isinstance(l, list), unified_structure)
        for unified_member in lst:
            if unified_member[0] == 'fieldRef':
                exclude_keys = ['textId', 'inlined', 'legacyIndent', 'legacyPosition', 'name', 'required']
                field_attr = {k: unified_member[1][k] for k in
                              set(list(unified_member[1].keys())) - set(exclude_keys)}
                field_attr['presence'] = Unified2Orchestra10.unified2orch_presence(unified_member[1].get('required', 0))
                field_ref = ['fixr:fieldRef', field_attr]
                structure.append(field_ref)
            elif unified_member[0] == 'componentRef':
                component_id = unified_member[1]['id']
                component = UnifiedMainInstance.component(fix, component_id)
                if component[1].get('repeating', 0) == 1:
                    exclude_keys = ['textId', 'inlined', 'legacyIndent', 'legacyPosition', 'name', 'required']
                    group_attr = {k: unified_member[1][k] for k in
                                  set(list(unified_member[1].keys())) - set(exclude_keys)}
                    group_attr['presence'] = Unified2Orchestra10.unified2orch_presence(
                        unified_member[1].get('required', 0))
                    group_ref = ['fixr:groupRef', group_attr]
                    structure.append(group_ref)
                else:
                    exclude_keys = ['textId', 'inlined', 'legacyIndent', 'legacyPosition', 'name', 'required']
                    component_attr = {k: unified_member[1][k] for k in
                                      set(list(unified_member[1].keys())) - set(exclude_keys)}
                    component_attr['presence'] = Unified2Orchestra10.unified2orch_presence(
                        unified_member[1].get('required', 0))
                    component_ref = ['fixr:componentRef', component_attr]
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
