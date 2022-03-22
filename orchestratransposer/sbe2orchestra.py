import logging
from typing import List

from orchestratransposer.orchestra.orchestra import Orchestra10WithSBE10Types, Orchestra10WithSBE20Types
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.sbe.sbe import SBE10, SBE20
from orchestratransposer.sbe.sbeinstance import SBEInstance10, SBEInstance20


class SBE2Orchestra10_10:
    """
    Translates between a Simple Binary Encoding message schema version 1.0 and
    an FIX Orchestra file version 1.0. Supports embedded SBE datatypes.
    """

    def __init__(self):
        self.logger = logging.getLogger('sbe2orchestra')
        self.max_id = 5000

    def sbe2orch_dict(self, sbe: SBEInstance10) -> OrchestraInstance10:
        """
        Translate an SBE message schema dictionary to an Orchestra dictionary
        :param sbe: an SBE version 1.0 data dictionary
        :return: an Orchestra version 1.0 data dictionary
        """
        orch = OrchestraInstance10()
        self.sbe2orch_metadata(sbe, orch)
        fields = orch.fields()
        self.sbe2orch_fields(sbe, fields)
        # add fields before composite datatypes because some composite members may become fields, but avoid dups
        self.sbe2orch_datatypes(sbe, orch)
        codesets = orch.codesets()
        self.sbe2orch_codesets(sbe, codesets)
        self.sbe2orch_messages_and_groups(sbe, orch)
        return orch

    def sbe2orch_xml(self, sbe_xml, orch_stream) -> List[Exception]:
        """
        Translate an SBE message schema into an Orchestra file
        :param sbe_xml: an XML file-like object in SBE schema
        :param orch_stream: an output stream to write an Orchestra file
        :return: a list of errors, if any
        """
        sbe = SBE10()
        (sbe_instance, errors) = sbe.read_xml(sbe_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orch_instance = self.sbe2orch_dict(sbe_instance)
            orchestra = Orchestra10WithSBE10Types()
            errors = orchestra.write_xml(orch_instance, orch_stream)
            if errors:
                for error in errors:
                    self.logger.error(error)
            return errors

    def sbe2orch_metadata(self, sbe: SBEInstance10, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from an SBE message schema
        """
        repository = orch.repository()
        ms = sbe.message_schema()
        repository['name'] = ms['package']
        orch.metadata().append(['dcterms:identifier', str(ms['id'])])
        # a simple integer is not accepted as version in Orchestra 1.0
        repository['version'] = str(ms['version']) + ".0"

    def sbe2orch_datatypes(self, sbe: SBEInstance10, orch: OrchestraInstance10):
        """
        Append Orchestra datatypes from SBE simple and composite types

        An SBE type can have 'semanticType' to map to FIX datatypes. It is optional, so mapping to a FIX datatype may
        not be provided. Moreover, multiple SBE types may map to single datatype in Orchestra, e.g. 32-  and 64-bit
        integers both map to 'int' FIX type. The Orchestra v1.0 schema does not handle this case. Therefore, each SBE
        type will be mapped to its own Orchestra datatype.
        """
        orch_datatypes = orch.datatypes()
        self.sbe2orch_simple_types(orch_datatypes, sbe)
        self.sbe2orch_composite_types(orch, sbe)

    def sbe2orch_composite_types(self, orch: OrchestraInstance10, sbe: SBEInstance10):
        """
        Adds SBE composite encoding types to Orchestra as components
        :param orchs: an Orchestra file
        :param sbe: an SBE message schema
        """
        sbe_composites = sbe.composites()
        fields = orch.fields()
        for sbe_composite in sbe_composites:
            sbe_name = sbe_composite[1]['name']
            sbe_field = sbe.first_field_by_type(sbe_name)
            if sbe_field:
                sbe_field_id = sbe_field[1]['id']
            else:
                self.max_id += 1
                sbe_field_id = self.max_id
            component_attr = {'name': sbe_name, 'id': sbe_field_id}
            component = ['fixr:component', component_attr]
            orch.append_component(component)
            # convert composite members to fields if they do not already exist from messages or groups
            sbe_types = filter(lambda t: isinstance(t, list), sbe_composite)
            for sbe_type in sbe_types:
                documentation = sbe_type[1].get('description', None)
                # Add as a field if it does not already exist
                field = orch.field_by_name(sbe_type[1]['name'])
                if field:
                    field_id = field[1]['id']
                else:
                    field_type = sbe_type[1].get('type', None)
                    if not field_type:
                        field_type = sbe_type[1].get('primitiveType', None)
                    self.max_id += 1
                    field_id = self.max_id
                    field_attr = {'id': field_id,
                                  'name': sbe_type[1]['name'],
                                  'type': field_type}
                    field = ['fixr:field', field_attr]
                    if documentation:
                        OrchestraInstance10.append_documentation(field, documentation)
                    fields.append(field)
                field_ref_attr = {'id': field_id}
                field_ref = ['fixr:fieldRef', field_ref_attr]
                if documentation:
                    OrchestraInstance10.append_documentation(field_ref, documentation)
                OrchestraInstance10.append_field_ref(component, field_ref)

    def sbe2orch_simple_types(self, orch_datatypes, sbe: SBEInstance10):
        """
        Adds all SBE simple encoding types to Orchestra as datatypes with mapping
        :param orch_datatypes: datatypes section of an Orchestra file
        :param sbe: an SBE message schema

        Workaround: since Orchestra mappedDatatype elements lacks a length attribute, parameter attribute is used to
        hold length. However, the datatype of parameter is string rather than numeric.
        """
        # add built-in primitive types
        for t in ['char', 'int8', 'int16', 'int32', 'int64',
                  'uint8', 'uint16', 'uint32', 'uint64', 'float', 'double']:
            sbe_type = ['type', {'name': t, 'primitiveType': t}]
            self.sbe2orch_simple_type(orch_datatypes, sbe_type)
        sbe_types = sbe.encoding_types()
        for sbe_type in sbe_types:
            self.sbe2orch_simple_type(orch_datatypes, sbe_type)

    def sbe2orch_simple_type(self, orch_datatypes, sbe_type):
        """
        Adds one SBE simple encoding types to Orchestra as datatypes with mapping
        :param orch_datatypes:
        :param sbe_type: an SBE simple type to transform and append to Orchestra datatypes
        """
        mapping_attr = {'standard': 'SBE', 'base': sbe_type[1]['primitiveType']}
        length = sbe_type[1].get('length', 0)
        if length > 0:
            mapping_attr['parameter'] = str(length)
        orch2sbe_mapping = ['fixr:mappedDatatype', mapping_attr]
        orch_datatype = ['fixr:datatype', {'name': sbe_type[1]['name']}, orch2sbe_mapping]
        orch_datatypes.append(orch_datatype)

    def sbe2orch_codesets(self, sbe: SBEInstance10, codesets: list):
        sbe_enums: list = sbe.enums()
        for idx, sbe_enum in enumerate(sbe_enums, start=1):
            codeset_attr = {'name': sbe_enum[1]['name'], 'id': idx * 100, 'type': sbe_enum[1]['encodingType']}
            codeset = ['fixr:codeSet', codeset_attr]
            documentation = sbe_enum[1].get('description', None)
            sbe_codes = filter(lambda c: isinstance(c, list) and c[0] == 'validValue', sbe_enum)
            for idx2, sbe_code in enumerate(sbe_codes, start=1):
                code_attr = {'name': sbe_code[1]['name'], 'id': idx * 100 + idx2, 'value': sbe_code[2]}
                code = ['fixr:code', code_attr]
                code_documentation = sbe_enum[1].get('description', None)
                if code_documentation:
                    OrchestraInstance10.append_documentation(code, code_documentation)
                codeset.append(code)
            if documentation:
                OrchestraInstance10.append_documentation(codeset, documentation)
            codesets.append(codeset)

    def sbe2orch_messages_and_groups(self, sbe: SBEInstance10, orch: OrchestraInstance10):
        sbe_messages = sbe.messages()
        for sbe_message in sbe_messages:
            msg_attr = {'name': sbe_message[1]['name'], 'id': sbe_message[1]['id']}
            msg = ['fixr:message', msg_attr]
            msg_type = sbe_message[1].get('semanticType', None)
            if msg_type:
                msg_attr['msgType'] = msg_type
            documentation = sbe_message[1].get('description', None)
            structure = OrchestraInstance10.structure(msg)
            sbe_grp_fields = sbe.fields(sbe_message)
            sbe_groups = sbe.groups(sbe_message)
            sbe_data_fields = sbe.data(sbe_message)
            self.sbe2orch_append_members(structure, sbe_grp_fields, sbe_groups, sbe_data_fields, sbe)
            if documentation:
                OrchestraInstance10.append_documentation(msg, documentation)
            orch.append_message(msg)

            if sbe_groups:
                for sbe_group in sbe_groups:
                    group_attr = {'name': sbe_group[1]['name'], 'id': sbe_group[1]['id']}
                    group = ['fixr:group', group_attr]
                    sbe_grp_fields = sbe.fields(sbe_group)
                    sbe_grp_groups = sbe.groups(sbe_group)
                    sbe_grp_data_fields = sbe.data(sbe_group)
                    self.sbe2orch_append_members(group, sbe_grp_fields, sbe_grp_groups, sbe_grp_data_fields, sbe)
                    orch.append_group(group)

    def sbe2orch_append_members(self, structure, sbe_fields, sbe_groups, sbe_data_fields, sbe: SBEInstance10, ):
        for sbe_field in sbe_fields:
            # could be a fieldRef or componentRef
            member_id = sbe_field[1]['id']
            member_name = sbe_field[1]['name']
            member_type = sbe_field[1]['type']
            sbe_composite = sbe.composite_by_name(member_type)
            if sbe_composite:
                composite_ref_attr = {'id': member_id,
                                      'presence': self.sbe2orch_presence(sbe_field[1].get('presence', 'required'))}
                composite_ref = ['fixr:componentRef', composite_ref_attr]
                documentation = sbe_field[1].get('description', None)
                if documentation:
                    OrchestraInstance10.append_documentation(composite_ref, documentation)
                OrchestraInstance10.append_field_ref(structure, composite_ref)
            else:
                field_ref_attr = {'id': member_id,
                                  'presence': self.sbe2orch_presence(sbe_field[1].get('presence', 'required'))}
                field_ref = ['fixr:fieldRef', field_ref_attr]
                documentation = sbe_field[1].get('description', None)
                if documentation:
                    OrchestraInstance10.append_documentation(field_ref, documentation)
                OrchestraInstance10.append_field_ref(structure, field_ref)
        if sbe_groups:
            for sbe_group in sbe_groups:
                group_ref_attr = {'id': sbe_group[1]['id']}
                group_ref = ['fixr:groupRef', group_ref_attr]
                documentation = sbe_group[1].get('description', None)
                if documentation:
                    OrchestraInstance10.append_documentation(group_ref, documentation)
                OrchestraInstance10.append_group_ref(structure, group_ref)
        if sbe_data_fields:
            for sbe_field in sbe_data_fields:
                field_ref_attr = {'id': sbe_field[1]['id'],
                                  'presence': self.sbe2orch_presence(sbe_field[1].get('presence', None))}
                field_ref = ['fixr:fieldRef', field_ref_attr]
                documentation = sbe_field[1].get('description', None)
                if documentation:
                    OrchestraInstance10.append_documentation(field_ref, documentation)
                OrchestraInstance10.append_field_ref(structure, field_ref)

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
                field_d[sbe_field[1]['id']] = sbe_field
            all_sbe_data_fields = []
            SBEInstance10.all_data(sbe_message, all_sbe_data_fields)
            for sbe_field in all_sbe_data_fields:
                field_d[sbe_field[1]['id']] = sbe_field
        field_l = sorted(field_d.values(), key=SBEInstance10.id)
        for sbe_field in field_l:
            field_attr = {'id': sbe_field[1]['id'],
                          'name': sbe_field[1]['name'],
                          'type': sbe_field[1]['type']}
            field = ['fixr:field', field_attr]
            documentation = sbe_field[1].get('description', None)
            if documentation:
                OrchestraInstance10.append_documentation(field, documentation)
            fields.append(field)

    @staticmethod
    def sbe2orch_presence(sbe_presence: str) -> str:
        """ Translate SBE presence to Orchestra presence string """
        if not sbe_presence or sbe_presence == 'optional':
            return 'optional'
        elif sbe_presence == 'constant':
            return 'constant'
        elif sbe_presence == 'required':
            return 'required'


SBE2Orchestra = SBE2Orchestra10_10
"""Translates Orchestra version 1.0 to SBE version 1.0"""


class SBE2Orchestra20_10(SBE2Orchestra10_10):

    def sbe2orch_dict(self, sbe: SBEInstance20) -> OrchestraInstance10:
        """
        Translate an SBE message schema dictionary to an Orchestra dictionary
        :param sbe: an SBE version 2.0 data dictionary
        :return: an Orchestra version 1.0 data dictionary
        """
        orch = OrchestraInstance10()
        self.sbe2orch_metadata(sbe, orch)
        codesets = orch.codesets()
        self.sbe2orch_codesets(sbe, codesets)
        fields = orch.fields()
        self.sbe2orch_fields(sbe, fields)
        self.sbe2orch_messages_and_groups(sbe, orch)
        # do last because some datatypes are converted to fields that may have already been defined in messages
        self.sbe2orch_datatypes(sbe, orch)
        return orch

    def sbe2orch_xml(self, sbe_xml, orch_stream) -> List[Exception]:
        """
        Translate an SBE message schema into an Orchestra file
        :param sbe_xml: an XML file-like object in SBE schema
        :param orch_stream: an output stream to write an Orchestra file
        :return: a list of errors, if any
        """
        sbe = SBE20()
        (sbe_instance, errors) = sbe.read_xml(sbe_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orch_instance = self.sbe2orch_dict(sbe_instance)
            orchestra = Orchestra10WithSBE20Types()
            errors = orchestra.write_xml(orch_instance, orch_stream)
            if errors:
                for error in errors:
                    self.logger.error(error)
            return errors
