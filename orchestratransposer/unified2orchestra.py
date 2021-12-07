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
        codesets = orch.codesets()
        self.unified2orch_codesets(fix, codesets)
        fields = orch.fields()
        self.unified2orch_fields(fix, fields)
        """self.unified2orch_messages_and_groups(fix, orch)"""
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

    def unified2orch_datatypes(self, fix: list, datatypes: list):
        unified_datatypes = UnifiedMainInstance.datatypes(fix)
        lst = filter(lambda l: isinstance(l, list) and l[0] == 'datatype', unified_datatypes)
        for unified_datatype in lst:
            exclude_keys = ['textId']
            datatype_attr = {k: unified_datatype[1][k] for k in set(list(unified_datatype[1].keys())) - set(exclude_keys)}
            datatype = ['fixr:datatype', datatype_attr]
            """ TODO annotations with example"""
            xml = next(filter(lambda l: isinstance(l, list) and l[0] == 'XML', unified_datatype), None)
            if xml:
                xml_mapping = ['fixr:mappedDatatype', {k: xml[1][k] for k in set(list(xml[1].keys())) - set(exclude_keys)}]
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


Unified2Orchestra = Unified2Orchestra10
""" Default implementation of Unified Repository to Orchestra conversion """
