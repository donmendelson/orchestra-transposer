import logging
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
        datatypes = orch.datatypes()
        self.unified2orch_datatypes(fix, datatypes)
        """codesets = orch.codesets()
        self.unified2orch_codesets(fix, codesets)"""
        fields = orch.fields()
        self.unified2orch_fields(fix, fields)
        """self.unified2orch_messages_and_groups(fix, orch)"""
        return orch

    def unified2orch_xml(self, xml_path, phrases_xml_path, orch_stream, version: Optional[str] = None) -> List[Exception]:
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

    def unified2orch_metadata(self, fix: dict, orch: OrchestraInstance10):
        """
        Set Orchestra metadata from a Unified Repository
        """
        repository = orch.root()
        repository['@name'] = fix['@version']
        version = str(fix['@version']).partition('_')[0]
        repository['@version'] = version

    def unified2orch_datatypes(self, fix: dict, datatypes):
        unified_datatypes = UnifiedMainInstance.datatypes(fix)
        for unified_datatype in unified_datatypes:
            exclude_keys = ['@textId', 'XML', 'Example']
            datatype = {k: unified_datatype[k] for k in set(list(unified_datatype.keys())) - set(exclude_keys)}
            """ TODO annotations with example"""
            xml = unified_datatype.get('XML', None)
            if xml:
                mappings = []
                orch2xml_mapping = {k: xml[k] for k in set(list(xml.keys())) - set(exclude_keys)}
                mappings.append(orch2xml_mapping)
                datatype['fixr:mappedDatatype'] = mappings
            datatypes.append(datatype)

    def unified2orch_fields(self, fix: dict, fields: list):
        unified_fields = UnifiedMainInstance.fields(fix)
        for unified_field in unified_fields:
            exclude_keys = ['@textId', '@notReqXML', 'enum', '@associatedDataTag', '@enumDatatype']
            field = {k: unified_field[k] for k in set(list(unified_field.keys())) - set(exclude_keys)}
            if 'enum' in unified_field:
                codeset_name = unified_field['@name']
                enum_id = unified_field.get('@enumDatatype', None)
                if enum_id:
                    enum_field = UnifiedMainInstance.field(fix, enum_id)
                    if enum_field:
                        codeset_name = enum_field['@name']
                field['@type'] = codeset_name + 'CodeSet'
            assoc_id = unified_field.get('@associatedDataTag', None)
            if assoc_id:
                assoc_field = UnifiedMainInstance.field(fix, assoc_id)
                if assoc_field:
                    field['lengthId'] = assoc_field['@id']
            fields.append(field)

Unified2Orchestra = Unified2Orchestra10
""" Default implementation of Unified Repository to Orchestra conversion """
