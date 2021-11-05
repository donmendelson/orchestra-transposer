import logging
from typing import List

from orchestratransposer.orchestra.orchestra import Orchestra10WithSBETypes
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.sbe.sbe import SBE10
from orchestratransposer.sbe.sbeinstance import SBEInstance10


TEXT_KEY = '$'
""" Symbol used by XMLSchema package for text content of an element (#text) """


class SBE2Orchestra10_10:

    def __init__(self):
        self.logger = logging.getLogger('sbe2orchestra')

    """
    Translates between a Simple Binary Encoding message schema version 1.0 and 
    an FIX Orchestra file version 1.0. Supports embedded SBE datatypes.
    """

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
        sbe = SBE10()
        (sbe_instance, errors) = sbe.read_xml(sbe_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orch_instance = self.sbe2orch_dict(sbe_instance)
            orchestra = Orchestra10WithSBETypes()
            errors = orchestra.write_xml(orch_instance, orch_stream)
            if errors:
                for error in errors:
                    self.logger.error(error)
            return errors

    def sbe2orch_metadata(self, sbe: SBEInstance10, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from an SBE message schema
        """
        repository = orch.root()
        sbe_ms = sbe.root()
        repository['@name'] = sbe_ms['@package']
        orch.metadata()['dcterms:identifier'] = str(sbe_ms['@id'])
        # a simple integer is not accepted as version in Orchestra 1.0
        repository['@version'] = str(sbe_ms['@version']) + ".0"

    def sbe2orch_datatypes(self, sbe: SBEInstance10, orch_datatypes: list):
        """
        Append Orchestra datatypes from SBE simple and composite types

        An SBE type can have 'semanticType' to map to FIX datatypes. It is optional, so mapping to a FIX datatype may
        not be provided. Moreover, multiple SBE types may map to single datatype in Orchestra, e.g. 32-  and 64-bit
        integers both map to 'int' FIX type. The Orchestra v1.0 schema does not handle this case. Therefore, each SBE
        type will be mapped to its own Orchestra datatype.
        """
        self.sbe2orch_simple_types(orch_datatypes, sbe)
        self.sbe2orch_composite_types(orch_datatypes, sbe)

    def sbe2orch_composite_types(self, orch_datatypes, sbe):
        sbe_composites = sbe.composites()
        for sbe_composite in sbe_composites:
            prefix_composite = self.__prefix_attributes('sbe', sbe_composite)
            extension = {'sbe:composite': [prefix_composite]}
            orch2sbe_mapping = {'@standard': 'SBE', 'fixr:extension': extension}
            orch_mappings = []
            orch_mappings.append(orch2sbe_mapping)
            orch_datatype = {'@name': sbe_composite['@name'], 'fixr:mappedDatatype': orch_mappings}
            orch_datatypes.append(orch_datatype)

    def sbe2orch_simple_types(self, orch_datatypes, sbe):
        sbe_types = sbe.encoding_types()
        for sbe_type in sbe_types:
            orch_mappings = []
            orch2sbe_mapping = {'@standard': 'SBE', '@base': sbe_type['@primitiveType']}
            orch_mappings.append(orch2sbe_mapping)
            orch_datatype = {'@name': sbe_type['@name'], 'fixr:mappedDatatype': orch_mappings}
            orch_datatypes.append(orch_datatype)

    def __prefix_attributes(self, prefix: str, attr: dict):
        prefixed = {}
        for (k, v) in attr.items():
            if k[0] == '@':
                prefixed['@'+prefix+':'+k[1:]] = v
            else:
                prefixed[prefix+':'+k] = v
        return prefixed

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
        field_l = sorted(field_d.values(), key=SBEInstance10.id)
        for sbe_field in field_l:
            field = {'@id': sbe_field['@id'],
                     '@name': sbe_field['@name'],
                     '@type': sbe_field['@type']}
            documentation = sbe_field.get('@description', None)
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
