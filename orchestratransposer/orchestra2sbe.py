import logging
from typing import List, Optional

from orchestratransposer.orchestra.orchestra import Orchestra10WithSBE10Types
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.sbe.sbe import SBE10
from orchestratransposer.sbe.sbeinstance import SBEInstance10


class Orchestra2SBE10_10:
    def __init__(self):
        self.logger = logging.getLogger('orchestra2sbe')

    def orch2sbe_dict(self, orch: OrchestraInstance10) -> SBEInstance10:
        """
        Translate an Orchestra dictionary to an SBE message schema dictionary
        :param orch: an Orchestra version 1.0 data dictionary
        :return: an SBE version 1.0 data dictionary
        """
        sbe = SBEInstance10()
        self.orch2sbe_metadata(orch, sbe)
        datatypes = orch.datatypes()
        self.orch2sbe_datatypes(datatypes, sbe)
        codesets = orch.codesets()
        self.orch2sbe_codesets(codesets, sbe)
        messages = orch.messages()
        self.orch2sbe_messages(messages, sbe, orch)
        return sbe

    def orch2sbe_xml(self, orchestra_xml, sbe_stream) -> List[Exception]:
        """
        Translate an Orchestra file to an SBE message schema file
        :param orchestra_xml: an XML file-like object in Orchestra schema
        :param sbe_stream: an output stream to write an SBE file
        :return: a list of errors, if any
        """
        # Supports embedded SBE encoding types in Orchestra datatypes
        orchestra = Orchestra10WithSBE10Types()
        (orch_instance, errors) = orchestra.read_xml(orchestra_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            sbe_instance = self.orch2sbe_dict(orch_instance)
            sbe = SBE10()
            errors = sbe.write_xml(sbe_instance, sbe_stream)
            for error in errors:
                self.logger.error(error)
            return errors

    def orch2sbe_metadata(self, orch: OrchestraInstance10, sbe: SBEInstance10):
        """
        Set SBE message schema metadata from Orchestra

        SBE schema id is derived from Orchestra metadata dcterms:identifier, defaults to 1.
        """
        repository = orch.repository()
        ms = sbe.message_schema()
        ms['package'] = repository.get('name', 'Unknown')
        metadata = orch.metadata()
        try:
            identifier = next(i for i in metadata if i[0] == 'dcterms:identifier')
            ms['id'] = int(identifier[1])
        except StopIteration:
            ms['id'] = 1
        ms['version'] = 0

    def orch2sbe_datatypes(self, datatypes: list, sbe: SBEInstance10):
        """
        Append SBE types from Orchestra datatypes
        """
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:datatype', datatypes)
        for datatype in lst:
            name = datatype[1]['name']
            if name not in ['NumInGroup', 'Length', 'Reserved100Plus', 'Reserved1000Plus', 'Reserved4000Plus', 'XID',
                            'XIDREF']:
                sbe_type_attr = {'name': name, 'semanticType': name}
                mappings = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:mappedDatatype', datatype)
                if mappings:
                    mapping = next(
                        (mapping for mapping in mappings if mapping[1]['standard'] == 'SBE'), None)
                    if mapping:
                        documentation = Orchestra2SBE10_10.__documentation_str(mapping)
                        if documentation:
                            sbe_type_attr['description'] = documentation
                        extension = next(
                            (i for i in mapping if isinstance(i, list) and i[0] == 'fixr:extension'), None)
                        if extension:
                            sbe_types = next(
                                (i for i in extension if isinstance(i, list) and i[2] == 'types'), None)
                            if sbe_types:
                                sbe_composite = sbe_types[0]
                                sbe.append_composite(sbe_composite)
                            else:
                                self.logger.error('SBE datatype mapping not found for name=%s', name)
                        else:
                            base = mapping[1].get('base', None)
                            if base:
                                sbe_type_attr['primitiveType'] = base
                            min_inclusive = mapping[1].get('minInclusive', None)
                            if min_inclusive:
                                sbe_type_attr['minValue'] = min_inclusive
                            max_inclusive = mapping[1].get('maxInclusive', None)
                            if max_inclusive:
                                sbe_type_attr['maxValue'] = max_inclusive
                            sbe_type = ['type', sbe_type_attr]
                            sbe.append_encoding_type(sbe_type)

    def orch2sbe_codesets(self, codesets: list, sbe: SBEInstance10):
        """
        Append SBE enums from Orchestra codesets
        """
        codeset_lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:codeSet', codesets)
        for codeset in codeset_lst:
            sbe_enum_attr = {'name': codeset[1]['name'], 'encodingType': codeset[1]['type']}
            documentation = Orchestra2SBE10_10.__documentation_str(codeset)
            if documentation:
                sbe_enum_attr['description'] = documentation
            sbe_enum = ['enum', sbe_enum_attr]
            cd_lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:code', codeset)
            for code in cd_lst:
                sbe_code = ['validValue']
                sbe_code_attr = {'name': code[1]['name']}
                sbe_code.append(sbe_code_attr)
                documentation = Orchestra2SBE10_10.__documentation_str(code)
                if documentation:
                    sbe_code_attr['description'] = documentation
                sbe_enum.append(sbe_code)
            sbe.append_enum(sbe_enum)

    @staticmethod
    def __documentation_str(element) -> Optional[str]:
        # Use first instance of possibly multiple documentations; consider concatenation
        try:
            documentation = OrchestraInstance10.documentation(element)
            return documentation[0][1]
        except IndexError:
            return None

    def orch2sbe_append_members(self, sbe_structure: list, field_refs, component_refs, group_refs, orch):
        """ Appends members to an SBE message or group structure from Orchestra """
        sbe_fields = []
        sbe_groups = []
        sbe_data = []
        self.orch2sbe_fields(sbe_fields, sbe_data, field_refs, orch)
        self.orch2sbe_components(sbe_fields, sbe_data, sbe_groups, component_refs, orch)
        self.orch2sbe_groups(sbe_groups, group_refs, orch)
        # Order must be fixed fields / groups / variable length data
        for field in sbe_fields:
            SBEInstance10.append_field(sbe_structure, field)
        for group in sbe_groups:
            SBEInstance10.append_group(sbe_structure, group)
        for data_field in sbe_data:
            SBEInstance10.append_data_field(sbe_structure, data_field)

    def orch2sbe_messages(self, messages: list, sbe: SBEInstance10, orch: OrchestraInstance10):
        """
        Append SBE messages from Orchestra
        """
        msg_lst = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:message', messages)
        for msg in msg_lst:
            sbe_msg = ['sbe:message']
            sbe_msg_attr = {'name': msg[1]['name'], 'id': msg[1]['id']}
            sbe_msg.append(sbe_msg_attr)
            msg_type = msg[1].get('msgType', None)
            if msg_type:
                sbe_msg_attr['semanticType'] = msg_type
            documentation = Orchestra2SBE10_10.__documentation_str(msg)
            if documentation:
                sbe_msg_attr['description'] = documentation
            structure = OrchestraInstance10.structure(msg)
            field_refs = OrchestraInstance10.field_refs(structure)
            component_refs = OrchestraInstance10.component_refs(structure)
            group_refs = OrchestraInstance10.group_refs(structure)
            self.orch2sbe_append_members(sbe_msg, field_refs, component_refs, group_refs, orch)
            sbe.append_message(sbe_msg)

    def orch2sbe_fields(self, sbe_fields: list, sbe_data: list, field_refs: list, orch: OrchestraInstance10):
        for field_ref in field_refs:
            field_id = field_ref[1]['id']
            field = orch.field(field_id)
            if field:
                name = field[1].get('name', 'Unknown')
                abbr_name = field[1].get('abbrName', None)
                if len(name) > 64:
                    if abbr_name:
                        name = abbr_name
                    else:
                        name = name[:64]
                    self.logger.warning('Field text_id=%d name=%s shortened to %s', field_id, field[1]['name'], name)
                presence = Orchestra2SBE10_10.orch2sbe_presence(field_ref[1].get('presence', None))
                field_type = field[1].get('type', 'Unknown')
                if field_type not in ['Length', 'NumInGroup']:
                    sbe_field_attr = {'id': field_id,
                                      'name': name,
                                      'presence': presence,
                                      'type': field_type}
                    documentation = Orchestra2SBE10_10.__documentation_str(field_ref)
                    if documentation:
                        sbe_field_attr['description'] = documentation
                    if field_type in ['data', 'XMLData']:
                        sbe_data_field = ['data', sbe_field_attr]
                        sbe_data.append(sbe_data_field)
                    else:
                        sbe_field = ['field', sbe_field_attr]
                        sbe_fields.append(sbe_field)
            else:
                self.logger.error('Field id=%d not found', field_id)
                sbe_field_attr = {'id': field_id,
                                  'name': 'Unknown',
                                  'presence': 'required',
                                  'type': 'Unknown'}
                sbe_field = ['field', sbe_field_attr]
                sbe_fields.append(sbe_field)

    def orch2sbe_components(self, sbe_fields: list, sbe_data: list, sbe_groups: list, component_refs: list,
                            orch: OrchestraInstance10):
        """
        Recursively expand an Orchestra component into its members

        Special case: do not expand StandardHeader or StandardTrailer
        :param sbe_groups: a List of SBE groups to append
        :param sbe_data: a List of SBE variable-length fields to append
        :param sbe_fields: a List of SBE fixed-length fields to append
        :param component_refs: a List of componentRefs contained by an Orchestra message or component
        :param orch: an Orchestra file
        :return:
        """
        for component_ref in component_refs:
            component_id = component_ref[1]['id']
            component = orch.component(component_id)
            if component:
                name = component[1].get('name', 'Unknown')
                if name not in ['StandardHeader', 'StandardTrailer']:
                    field_refs = OrchestraInstance10.field_refs(component)
                    self.orch2sbe_fields(sbe_fields, sbe_data, field_refs, orch)
                    nested_component_refs = OrchestraInstance10.component_refs(component)
                    self.orch2sbe_components(sbe_fields, sbe_data, sbe_groups, nested_component_refs, orch)
                    group_refs = OrchestraInstance10.group_refs(component)
                    self.orch2sbe_groups(sbe_groups, group_refs, orch)
            else:
                self.logger.error('Component id=%d not found', component_id)

    def orch2sbe_groups(self, sbe_groups, group_refs, orch):
        """
        Append repeating groups to a message or outer group
        :param sbe_groups: a List of SBE groups to append
        :param group_refs: a List of groupsRefs contained by an Orchestra message or component
        :param orch: an Orchestra file
        :return:
        """
        for group_ref in group_refs:
            group_id = group_ref[1]['id']
            group = orch.group(group_id)
            if group:
                name = group[1].get('name', 'Unknown')
                abbr_name = group[1].get('abbrName', None)
                if len(name) > 64:
                    if abbr_name:
                        name = abbr_name
                    else:
                        name = name[:64]
                    self.logger.warning('Group text_id=%d name=%s shortened to %s', group_id, group[1]['name'], name)
                if group:
                    sbe_group = ['group']
                    sbe_group_attr = {'id': group_id,
                                      'name': name}
                    sbe_group.append(sbe_group_attr)
                    documentation = Orchestra2SBE10_10.__documentation_str(group)
                    if documentation:
                        sbe_group_attr['description'] = documentation
                    sbe_groups.append(sbe_group)
                    field_refs = OrchestraInstance10.field_refs(group)
                    component_refs = OrchestraInstance10.component_refs(group)
                    group_refs = OrchestraInstance10.group_refs(group)
                    self.orch2sbe_append_members(sbe_group, field_refs, component_refs, group_refs, orch)
            else:
                self.logger.error('Group id=%d not found', group_id)

    @staticmethod
    def orch2sbe_presence(orch_presence: Optional[str]) -> str:
        """ Translate Orchestra presence to SBE presence string """
        if not orch_presence or orch_presence == 'required':
            return 'required'
        elif orch_presence == 'constant':
            return 'constant'
        else:
            return 'optional'


Orchestra2SBE = Orchestra2SBE10_10
"""Translates Orchestra version 1.0 to SBE version 1.0"""
