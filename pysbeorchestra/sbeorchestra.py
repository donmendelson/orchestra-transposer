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

    def orchestra2sbe(self, orchestra_xml, sbe_stream) -> List[ValueError]:
        (data, errors) = self.orchestra.to_instance(orchestra_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            translate_errors = []
            orchestra_dict = data[0]
            sbe_instance = self.orchestra_dict2sbe_dict(orchestra_dict)
            self.sbe.write_instance(sbe_instance, sbe_stream)
            return translate_errors

    def orchestra_dict2sbe_dict(self, orch: OrchestraInstance) -> SBEInstance:
        sbe = SBEInstance()
        sbe_ms = sbe.root()
        repository = orch.root()
        self.orch2sbe_metadata(repository, sbe_ms)
        sbe_all_types = {}
        sbe_ms['types'] = sbe_all_types
        datatypes = repository['fixr:datatypes']
        self.orch2sbe_datatypes(datatypes, sbe_all_types)
        codesets = repository['fixr:codeSets']
        self.orch2sbe_codesets(codesets, sbe_all_types)
        return sbe

    def orch2sbe_metadata(self, repository, sbe_ms):
        """
        Set SBE message schema metadata from Orchestra
        """
        sbe_ms['@package'] = repository['@name']
        sbe_ms['@id'] = 1
        sbe_ms['@version'] = 0

    def orch2sbe_datatypes(self, datatypes, sbe_all_types):
        """
        Append SBE types from Orchesta datatypes
        """
        sbe_types = []
        sbe_all_types['type'] = sbe_types
        dt_lst = datatypes['fixr:datatype']
        for datatype in dt_lst:
            sbe_type_attr = {}
            sbe_type_attr['@name'] = datatype['@name']
            sbe_type_attr['@semanticType'] = datatype['@name']
            mappings = datatype.get('fixr:mappedDatatype', None)
            if mappings:
                mapping = next(
                    (mapping for mapping in mappings if mapping['@standard'] == 'SBE'), None)
                if (mapping):
                    sbe_type_attr['@primitiveType'] = mapping['@base']
                    sbe_type_attr['minValue'] = mapping['minInclusive']
                    sbe_type_attr['maxValue'] = mapping['maxInclusive']
            sbe_types.append(sbe_type_attr)

    def orch2sbe_codesets(self, codesets, sbe_all_types):
        """
        Append SBE enums from Orchesta codesets
        """
        sbe_enums = []
        sbe_all_types['enum'] = sbe_enums
        cs_lst = codesets['fixr:codeSet']
        for codeset in cs_lst:
            sbe_enum_attr = {}
            sbe_enum_attr['@name'] = codeset['@name']
            sbe_enum_attr['@encodingType'] = codeset['@type']
            sbe_codes = []
            sbe_enum_attr['validValue'] = sbe_codes
            cd_lst = codeset['fixr:code']
            for code in cd_lst:
                sbe_code_attr = {}
                sbe_code_attr['@name'] = code['@name']
                # $ represents element text
                sbe_code_attr['$'] = code['@value']
                sbe_codes.append(sbe_code_attr)

            sbe_enums.append(sbe_enum_attr)
