import logging
from typing import List

from orchestratransposer.orchestra.orchestra import Orchestra10
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.sbe.sbe import SBE10
from orchestratransposer.sbe.sbeinstance import SBEInstance10


TEXT_KEY = '$'
""" Symbol used by XMLSchema package for text content of an element (#text) """


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
        orchestra = Orchestra10()
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
        repository = orch.root()
        sbe_ms = sbe.root()
        sbe_ms['@package'] = repository.get('@name', 'Unknown')
        sbe_ms['@id'] = int(orch.metadata().get('dcterms:identifier', 1))
        sbe_ms['@version'] = 0

    def orch2sbe_datatypes(self, datatypes: list, sbe: SBEInstance10):
        """
        Append SBE types from Orchestra datatypes
        """
        for datatype in datatypes:
            name = datatype['@name']
            if name not in ['NumInGroup', 'Length', 'Reserved100Plus', 'Reserved1000Plus', 'Reserved4000Plus', 'XID',
                            'XIDREF']:
                sbe_type_attr = {'@name': name, '@semanticType': datatype['@name']}
                mappings = datatype.get('fixr:mappedDatatype', None)
                if mappings:
                    mapping = next(
                        (mapping for mapping in mappings if mapping['@standard'] == 'SBE'), None)
                    if mapping:
                        sbe_encoding = mapping.get('fixr:extension', None)
                        documentation = OrchestraInstance10.documentation(mapping)
                        if documentation:
                            sbe_type_attr['@description'] = documentation
                        if sbe_encoding:
                            try:
                                sbe_schema = sbe_encoding['sbe:messageSchema'][0]
                                sbe_types = sbe_schema['types'][0]
                                sbe_composite = sbe_types['composite'][0]
                                sbe.append_composite(sbe_composite)
                            except AttributeError:
                                self.logger.error('SBE datatype mapping not found for name=%s', name)
                        else:
                            base = mapping.get('@base', None)
                            if base:
                                sbe_type_attr['@primitiveType'] = base
                            min_inclusive = mapping.get('@minInclusive', None)
                            if min_inclusive:
                                sbe_type_attr['minValue'] = min_inclusive
                            max_inclusive = mapping.get('@maxInclusive', None)
                            if max_inclusive:
                                sbe_type_attr['maxValue'] = max_inclusive
                            sbe.append_encoding_type(sbe_type_attr)

    def orch2sbe_codesets(self, codesets: list, sbe: SBEInstance10):
        """
        Append SBE enums from Orchestra codesets
        """
        for codeset in codesets:
            sbe_enum_attr = {'@name': codeset['@name'], '@encodingType': codeset['@type']}
            documentation = OrchestraInstance10.documentation(codeset)
            if documentation:
                sbe_enum_attr['@description'] = documentation
            sbe_codes = []
            sbe_enum_attr['validValue'] = sbe_codes
            cd_lst = codeset['fixr:code']
            for code in cd_lst:
                sbe_code_attr = {'@name': code['@name'], TEXT_KEY: code['@value']}
                documentation = OrchestraInstance10.documentation(code)
                if documentation:
                    sbe_code_attr['@description'] = documentation
                sbe_codes.append(sbe_code_attr)

            sbe.append_enum(sbe_enum_attr)

    def orch2sbe_append_members(self, sbe_structure, field_refs, component_refs, group_refs, orch):
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
        for msg in messages:
            sbe_msg_attr = {'@name': msg['@name'], '@id': msg['@id']}
            msg_type = msg.get('@msgType', None)
            if msg_type:
                sbe_msg_attr['@semanticType'] = msg_type
            documentation = OrchestraInstance10.documentation(msg)
            if documentation:
                sbe_msg_attr['@description'] = documentation
            structure = OrchestraInstance10.structure(msg)
            field_refs = OrchestraInstance10.field_refs(structure)
            component_refs = OrchestraInstance10.component_refs(structure)
            group_refs = OrchestraInstance10.group_refs(structure)
            self.orch2sbe_append_members(sbe_msg_attr, field_refs, component_refs, group_refs, orch)
            sbe.append_message(sbe_msg_attr)

    def orch2sbe_fields(self, sbe_fields: list, sbe_data: list, field_refs: list, orch: OrchestraInstance10):
        for field_ref in field_refs:
            field_id = field_ref['@id']
            field = orch.field(field_id)
            name = field['@name'] if field else 'Unknown'
            abbr_name = field.get('@abbrName', None)
            if len(name) > 64:
                if abbr_name:
                    name = abbr_name
                else:
                    name = name[:64]
                self.logger.warning('Field id=%d name=%s shortened to %s', field_id, field['@name'], name)
            presence = Orchestra2SBE10_10.orch2sbe_presence(field_ref['@presence']) if field else 'required'
            field_type = field['@type'] if field else 'Unknown'
            if field_type not in ['Length', 'NumInGroup']:
                sbe_field_attr = {'@id': field_id,
                                  '@name': name,
                                  '@presence': presence,
                                  '@type': field_type}
                documentation = OrchestraInstance10.documentation(field_ref)
                if documentation:
                    sbe_field_attr['@description'] = documentation
                if field_type == 'data':
                    sbe_data.append(sbe_field_attr)
                else:
                    sbe_fields.append(sbe_field_attr)
            else:
                self.logger.warning('Field id=%d name=%s not defined', field_id, name)

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
            component_id = component_ref['@id']
            component = orch.component(component_id)
            name = component['@name'] if component else 'Unknown'
            if component and name not in ['StandardHeader', 'StandardTrailer']:
                field_refs = OrchestraInstance10.field_refs(component)
                self.orch2sbe_fields(sbe_fields, sbe_data, field_refs, orch)
                nested_component_refs = OrchestraInstance10.component_refs(component)
                self.orch2sbe_components(sbe_fields, sbe_data, sbe_groups, nested_component_refs, orch)
                group_refs = OrchestraInstance10.group_refs(component)
                self.orch2sbe_groups(sbe_groups, group_refs, orch)
            else:
                self.logger.warning('Component id=%d name=%s not defined', component_id, name)

    def orch2sbe_groups(self, sbe_groups, group_refs, orch):
        """
        Append repeating groups to a message or outer group
        :param sbe_groups: a List of SBE groups to append
        :param group_refs: a List of groupsRefs contained by an Orchestra message or component
        :param orch: an Orchestra file
        :return:
        """
        for group_ref in group_refs:
            group_id = group_ref['@id']
            group = orch.group(group_id)
            name = group['@name'] if group else 'Unknown'
            abbr_name = group.get('@abbrName', None)
            if len(name) > 64:
                if abbr_name:
                    name = abbr_name
                else:
                    name = name[:64]
                self.logger.warning('Group id=%d name=%s shortened to %s', group_id, group['@name'], name)
            if group:
                sbe_group_attr = {'@id': group_ref['@id'],
                                  '@name': name}
                documentation = OrchestraInstance10.documentation(group)
                if documentation:
                    sbe_group_attr['@description'] = documentation
                sbe_groups.append(sbe_group_attr)
                field_refs = OrchestraInstance10.field_refs(group)
                component_refs = OrchestraInstance10.component_refs(group)
                group_refs = OrchestraInstance10.group_refs(group)
                self.orch2sbe_append_members(sbe_group_attr, field_refs, component_refs, group_refs, orch)
            else:
                self.logger.warning('Group id=%d name=%s not defined', group_id, name)

    @staticmethod
    def orch2sbe_presence(orch_presence: str) -> str:
        """ Translate Orchestra presence to SBE presence string """
        if not orch_presence or orch_presence == 'required':
            return 'required'
        elif orch_presence == 'constant':
            return 'constant'
        else:
            return 'optional'


Orchestra2SBE = Orchestra2SBE10_10
"""Translates Orchestra version 1.0 to SBE version 1.0"""
