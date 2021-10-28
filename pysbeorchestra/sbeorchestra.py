import logging
from typing import List

from pysbeorchestra import Orchestra, OrchestraInstance, SBE, SBEInstance


class SBEOrchestraTranslator:
    """
    Translates between a Simple Binary Encoding message schema version 1.0 and 
    an FIX Orchestra file version 1.0.
    """

    def __init__(self):
        self.logger = logging.getLogger('SBEOrchestraTranslator')
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
            translate_errors = []
            sbe_instance = self.orchestra_2sbe_dict(orch_instance)
            self.sbe.write_xml(sbe_instance, sbe_stream)
            return translate_errors

    def orchestra_2sbe_dict(self, orch: OrchestraInstance) -> SBEInstance:
        sbe = SBEInstance()
        self.orch2sbe_metadata(orch, sbe)
        datatypes = orch.datatypes()
        self.orch2sbe_datatypes(datatypes, sbe)
        codesets = orch.codesets()
        self.orch2sbe_codesets(codesets, sbe)
        messages = orch.messages()
        self.orch2sbe_messages(messages, sbe)
        return sbe

    def orch2sbe_metadata(self, orch: OrchestraInstance, sbe: SBEInstance):
        """
        Set SBE message schema metadata from Orchestra
        """
        repository = orch.root()
        sbe_ms = sbe.root()
        sbe_ms['@package'] = repository.get('@name', 'Unknown')
        sbe_ms['@id'] = 1
        sbe_ms['@version'] = 0

    def orch2sbe_datatypes(self, datatypes: list, sbe: SBEInstance):
        """
        Append SBE types from Orchestra datatypes
        """
        for datatype in datatypes:
            sbe_type_attr = {'@name': datatype['@name'], '@semanticType': datatype['@name']}
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
                    minInclusive = mapping.get('@minInclusive', None)
                    if minInclusive:
                        sbe_type_attr['minValue'] = minInclusive
                    maxInclusive = mapping.get('@maxInclusive', None)
                    if maxInclusive:
                        sbe_type_attr['maxValue'] = maxInclusive
            sbe.append_encoding_type(sbe_type_attr)

    def orch2sbe_codesets(self, codesets: list, sbe: SBEInstance):
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

    def orch2sbe_messages(self, messages: list, sbe: SBEInstance):
        """
        Append SBE messages from Orchestra
        """
        for msg in messages:
            sbe_msg_attr = {'@name': msg['@name'], '@id': msg['@id'], '@semanticType': msg['@msgType']}
            sbe.append_message(sbe_msg_attr)
