import logging
from typing import List

from orchestratransposer import Orchestra, SBE
from orchestratransposer.orchestra.orchestrainstance import OrchestraInstance10
from orchestratransposer.sbe.sbeinstance import SBEInstance10


class SBEOrchestraTransposer10_10:
    """
    Translates between a Simple Binary Encoding message schema version 1.0 and 
    an FIX Orchestra file version 1.0.
    """

    def __init__(self):
        self.logger = logging.getLogger('SBEOrchestraTransposer')
        self.orchestra = Orchestra()
        self.sbe = SBE()

    def orchestra2sbe_xml(self, orchestra_xml, sbe_stream) -> List[ValueError]:
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
            sbe_instance = self.orchestra_2sbe_dict(orch_instance)
            return self.sbe.write_xml(sbe_instance, sbe_stream)

    def orchestra_2sbe_dict(self, orch: OrchestraInstance10) -> SBEInstance10:
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

    def orch2sbe_metadata(self, orch: OrchestraInstance10, sbe: SBEInstance10):
        """
        Set SBE message schema metadata from Orchestra
        """
        repository = orch.root()
        sbe_ms = sbe.root()
        sbe_ms['@package'] = repository.get('@name', 'Unknown')
        sbe_ms['@id'] = 1
        sbe_ms['@version'] = 0

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
                sbe.append_encoding_type(sbe_type_attr)

    def orch2sbe_codesets(self, codesets: list, sbe: SBEInstance10):
        """
        Append SBE enums from Orchestra codesets
        """
        for codeset in codesets:
            sbe_enum_attr = {'@name': codeset['@name'], '@encodingType': codeset['@type']}
            sbe_codes = []
            sbe_enum_attr['validValue'] = sbe_codes
            cd_lst = codeset['fixr:code']
            for code in cd_lst:
                sbe_code_attr = {'@name': code['@name'], '$': code['@value']}
                # $ represents element text
                sbe_codes.append(sbe_code_attr)

            sbe.append_enum(sbe_enum_attr)

    def orch2sbe_messages(self, messages: list, sbe: SBEInstance10, orch: OrchestraInstance10):
        """
        Append SBE messages from Orchestra
        """
        for msg in messages:
            sbe_msg_attr = {'@name': msg['@name'], '@id': msg['@id'], '@semanticType': msg['@msgType']}
            structure = OrchestraInstance10.structure(msg)
            field_refs = OrchestraInstance10.field_refs(structure)
            component_refs = OrchestraInstance10.component_refs(structure)
            group_refs = OrchestraInstance10.group_refs(structure)
            self.append_members(sbe_msg_attr, field_refs, component_refs, group_refs, orch)
            sbe.append_message(sbe_msg_attr)

    def append_members(self, sbe_structure, field_refs, component_refs, group_refs, orch):
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
                if field_type == 'data':
                    sbe_data.append(sbe_field_attr)
                else:
                    sbe_fields.append(sbe_field_attr)
            else:
                self.logger.error('Field id=%d not found', field_id)

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
            group_id = group_ref['@id']
            group = orch.group(group_id)
            name = group['@name'] if group else 'Unknown'
            if group:
                sbe_group_attr = {'@id': group_ref['@id'],
                                  '@name': name}
                sbe_groups.append(sbe_group_attr)
                field_refs = OrchestraInstance10.field_refs(group)
                component_refs = OrchestraInstance10.component_refs(group)
                group_refs = OrchestraInstance10.group_refs(group)
                self.append_members(sbe_group_attr, field_refs, component_refs, group_refs, orch)
            else:
                self.logger.error('Group id=%d not found', group_id)

    @staticmethod
    def orch2sbe_presence(orch_presence: str) -> str:
        """ Translate Orchestra presence to SBE presence string """
        if not orch_presence or orch_presence == 'required':
            return 'required'
        elif orch_presence == 'constant':
            return 'constant'
        else:
            return 'optional'


SBEOrchestraTransposer = SBEOrchestraTransposer10_10
"""Translates between SBE version 1.0 and Orchestra version 1.0"""
