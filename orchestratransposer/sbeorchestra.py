import logging
from typing import List

from orchestratransposer import Orchestra, SBE
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.sbe.sbeinstance import SBEInstance10

TEXT_KEY = '$'
""" Symbol used by XMLSchema package for text content of an element (#text) """


class SBEOrchestraTransposer10_10:
    """
    Translates between a Simple Binary Encoding message schema version 1.0 and 
    an FIX Orchestra file version 1.0.
    """

    def __init__(self):
        self.logger = logging.getLogger('SBEOrchestraTransposer')
        self.orchestra = Orchestra()
        self.sbe = SBE()

    def orch2sbe_xml(self, orchestra_xml, sbe_stream) -> List[ValueError]:
        """
        Translate an Orchestra file to an SBE message schema file
        :param orchestra_xml: an XML file-like object in Orchestra schema
        :param sbe_stream: an output stream to write an SBE file
        :return: a list of errors, if any
        """
        (orch_instance, errors) = self.orchestra.read_xml(orchestra_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            sbe_instance = self.orch2sbe_dict(orch_instance)
            return self.sbe.write_xml(sbe_instance, sbe_stream)

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

    def sbe2orch_dict(self, sbe: SBEInstance10) -> OrchestraInstance10:
        """
        Translate an SBE message schema dictionary to an Orchestra dictionary
        :param sbe: an SBE version 1.0 data dictionary
        :return: an Orchestra version 1.0 data dictionary
        """
        orch = OrchestraInstance10()
        self.sbe2orch_metadata(sbe, orch)
        datatypes = orch.datatypes()
        self.sbe2orch_datatypes(sbe, datatypes)
        codesets = orch.codesets()
        self.sbe2orch_codesets(sbe, codesets)
        fields = orch.fields()
        self.sbe2orch_fields(sbe, fields)
        self.sbe2orch_messages_and_groups(sbe, orch)
        return orch

    def sbe2orch_xml(self, sbe_xml, orch_stream) -> List[ValueError]:
        """
        Translate an SBE message schema into an Orchestra file
        :param sbe_xml: an XML file-like object in SBE schema
        :param orch_stream: an output stream to write an Orchestra file
        :return: a list of errors, if any
        """
        (sbe_instance, errors) = self.sbe.read_xml(sbe_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orch_instance = self.sbe2orch_dict(sbe_instance)
            return self.orchestra.write_xml(orch_instance, orch_stream)

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

    def sbe2orch_metadata(self, sbe: SBEInstance10, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from an SBE message schema
        """
        repository = orch.root()
        sbe_ms = sbe.root()
        repository['@name'] = sbe_ms['@package']
        orch.metadata()['dcterms:identifier'] = str(sbe_ms['@id'])
        repository['@version'] = str(sbe_ms['@version'])

    def orch2sbe_datatypes(self, datatypes: list, sbe: SBEInstance10):
        """
        Append SBE types from Orchestra datatypes
        """
        for datatype in datatypes:
            name = datatype['@name']
            if name not in ['NumInGroup', 'Length', 'Reserved100Plus', 'Reserved1000Plus', 'Reserved4000Plus', 'XID',
                            'XIDREF']:
                sbe_type_attr = {'@name': name, '@semanticType': datatype['@name'], '@primitiveType': 'int64'}
                mappings = datatype.get('fixr:mappedDatatype', None)
                if mappings:
                    mapping = next(
                        (mapping for mapping in mappings if mapping['@standard'] == 'SBE'), None)
                    if mapping:
                        # sbe_encoding = mapping.get('fixr:extension', None)
                        # if sbe_encoding:
                        #    print(sbe_encoding)
                        # else:
                        base = mapping.get('@base', None)
                        if base:
                            sbe_type_attr['@primitiveType'] = base
                        min_inclusive = mapping.get('@minInclusive', None)
                        if min_inclusive:
                            sbe_type_attr['minValue'] = min_inclusive
                        max_inclusive = mapping.get('@maxInclusive', None)
                        if max_inclusive:
                            sbe_type_attr['maxValue'] = max_inclusive
                        documentation = OrchestraInstance10.documentation(mapping)
                        if documentation:
                            sbe_type_attr['@description'] = documentation
                sbe.append_encoding_type(sbe_type_attr)

    def sbe2orch_datatypes(self, sbe: SBEInstance10, orch_datatypes: list):
        """
        Append Orchestra datatypes from SBE simple and composite types

        An SBE type can have 'semanticType' to map to FIX datatypes. It is optional, so mapping to a FIX datatype may
        not be provided. Moreover, multiple SBE types may map to single datatype in Orchestra, e.g. 32-  and 64-bit
        integers both map to 'int' FIX type. The Orchestra v1.0 schema does not handle this case. Therefore, each SBE
        type will be mapped to its own Orchestra datatype.
        """
        sbe_types = sbe.encoding_types()
        for sbe_type in sbe_types:
            orch_mappings = []
            orch2sbe_mapping = {'@standard': 'SBE', '@base': sbe_type['@primitiveType']}
            orch_mappings.append(orch2sbe_mapping)
            orch_datatype = {'@name': sbe_type['@name'], 'fixr:mappedDatatype': orch_mappings}
            orch_datatypes.append(orch_datatype)

        sbe_composites = sbe.composites()
        for sbe_composite in sbe_composites:
            orch_mappings = []
            orch2sbe_mapping = {'@standard': 'SBE', 'fixr:extension': sbe_composite}
            orch_mappings.append(orch2sbe_mapping)
            orch_datatype = {'@name': sbe_composite['@name'], 'fixr:mappedDatatype': orch_mappings}
            orch_datatypes.append(orch_datatype)

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

    def sbe2orch_codesets(self, sbe: SBEInstance10, codesets: list):
        sbe_enums: list = sbe.enums()
        for idx, sbe_enum in enumerate(sbe_enums, start=1):
            codes = []
            codeset_attr = {'@name': sbe_enum['@name'], '@id': idx * 100, '@type': sbe_enum['@encodingType'],
                            'fixr:code': codes}
            documentation = sbe_enum.get('@description', None)
            if documentation:
                OrchestraInstance10.append_documentation(codeset_attr, documentation)
            sbe_codes = sbe_enum['validValue']
            for idx2, sbe_code in enumerate(sbe_codes, start=1):
                code_attr = {'@name': sbe_code['@name'], '@id': idx * 100 + idx2, '@value': sbe_code[TEXT_KEY]}
                documentation = sbe_enum.get('@description', None)
                if documentation:
                    OrchestraInstance10.append_documentation(code_attr, documentation)
                codes.append(code_attr)
            codesets.append(codeset_attr)

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

    def sbe2orch_messages_and_groups(self, sbe: SBEInstance10, orch: OrchestraInstance10):
        sbe_messages = sbe.messages()
        for sbe_message in sbe_messages:
            msg_attr = {'@name': sbe_message['@name'], '@id': sbe_message['@id']}
            msg_type = sbe_message.get('@semanticType', None)
            if msg_type:
                msg_attr['@msgType'] = msg_type
            documentation = sbe_message.get('@description', None)
            if documentation:
                OrchestraInstance10.append_documentation(msg_attr, documentation)
            structure = OrchestraInstance10.structure(msg_attr)
            sbe_fields = sbe.fields(sbe_message)
            sbe_groups = sbe.groups(sbe_message)
            sbe_data_fields = sbe.data(sbe_message)
            self.sbe2orch_append_members(structure, sbe_fields, sbe_groups, sbe_data_fields)
            orch.append_message(msg_attr)

            for sbe_group in sbe_groups:
                group_attr = {'@name': sbe_group['@name'], '@id': sbe_group['@id']}
                sbe_fields = sbe.fields(sbe_group)
                sbe_groups = sbe.groups(sbe_group)
                sbe_data_fields = sbe.data(sbe_group)
                self.sbe2orch_append_members(group_attr, sbe_fields, sbe_groups, sbe_data_fields)
                orch.append_group(group_attr)

    def sbe2orch_append_members(self, structure, sbe_fields, sbe_groups, sbe_data_fields):
        for sbe_field in sbe_fields:
            field_ref_attr = {'@id': sbe_field['@id'], '@presence': self.sbe2orch_presence(sbe_field['@presence'])}
            documentation = sbe_field.get('@description', None)
            if documentation:
                OrchestraInstance10.append_documentation(field_ref_attr, documentation)
            OrchestraInstance10.append_field_ref(structure, field_ref_attr)
        for sbe_group in sbe_groups:
            group_ref_attr = {'@id': sbe_group['@id']}
            documentation = sbe_group.get('@description', None)
            if documentation:
                OrchestraInstance10.append_documentation(group_ref_attr, documentation)
            OrchestraInstance10.append_group_ref(structure, group_ref_attr)
        for sbe_field in sbe_data_fields:
            field_ref_attr = {'@id': sbe_field['@id'], '@presence': self.sbe2orch_presence(sbe_field['@presence'])}
            documentation = sbe_field.get('@description', None)
            if documentation:
                OrchestraInstance10.append_documentation(field_ref_attr, documentation)
            OrchestraInstance10.append_field_ref(structure, field_ref_attr)

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

    def orch2sbe_fields(self, sbe_fields: list, sbe_data: list, field_refs: list, orch: OrchestraInstance10):
        for field_ref in field_refs:
            field_id = field_ref['@id']
            field = orch.field(field_id)
            name = field['@name'] if field else 'Unknown'
            presence = SBEOrchestraTransposer.orch2sbe_presence(field_ref['@presence']) if field else 'required'
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

    def sbe2orch_fields(self, sbe: SBEInstance10, fields: list):
        """
        Append unique fields from all SBE messages, by field id
        :param sbe: an SBE instance
        :param fields: Orchestra field list to populate
        :return:
        """
        field_d = {}
        sbe_messages: list = sbe.messages()
        for sbe_message in sbe_messages:
            all_sbe_fields = []
            SBEInstance10.all_fields(sbe_message, all_sbe_fields)
            for sbe_field in all_sbe_fields:
                field_d[sbe_field['@id']] = sbe_field
            all_sbe_data_fields = []
            SBEInstance10.all_data(sbe_message, all_sbe_data_fields)
            for sbe_field in all_sbe_data_fields:
                field_d[sbe_field['@id']] = sbe_field
                documentation = sbe_field.get('@description', None)
        field_l = sorted(field_d.values(), key=SBEInstance10.id)
        for sbe_field in field_l:
            field = {'@id': sbe_field['@id'],
                     '@name': sbe_field['@name'],
                     '@type': sbe_field['@type']}
            fields.append(field)

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

    @staticmethod
    def sbe2orch_presence(sbe_presence: str) -> str:
        """ Translate SBE presence to Orchestra presence string """
        if not sbe_presence or sbe_presence == 'optional':
            return 'optional'
        elif sbe_presence == 'constant':
            return 'constant'
        elif sbe_presence == 'required':
            return 'required'


SBEOrchestraTransposer = SBEOrchestraTransposer10_10
"""Translates between SBE version 1.0 and Orchestra version 1.0"""
