from pprint import pformat
from typing import Union


class OrchestraInstance10:
    """
    An instance of Orchestra version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj)

    def root(self) -> dict:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def metadata(self) -> dict:
        """
        :return: the metadata section of an Orchestra instance containing Dublin Core Terms
        """
        return self.obj.get("fixr:metadata", None)

    def datatypes(self) -> list:
        """
        :return: a list of  datatypes of an Orchestra instance
        """
        datatypes = self.obj.get('fixr:datatypes', None)
        if not datatypes:
            datatypes = {}
            self.obj['fixr:datatypes'] = datatypes
        datatype = datatypes.get('fixr:datatype', None)
        if not datatype:
            datatype = []
            datatypes['fixr:datatype'] = datatype
        return datatype

    def codesets(self) -> list:
        """
        :return: a list of  codesets of an Orchestra instance
        """
        codesets = self.obj.get('fixr:codeSets', None)
        if not codesets:
            codesets = {}
            self.obj['fixr:datatypes'] = codesets
        codeset = codesets.get('fixr:codeSet', None)
        if not codeset:
            codeset = []
            codesets['fixr:codeSet'] = codeset
        return codeset

    def fields(self) -> list:
        """
        :return: a list of  fields of an Orchestra instance
        """
        fields = self.obj.get('fixr:fields', None)
        if not fields:
            fields = {}
            self.obj['fixr:fields'] = fields
        field = fields.get('fixr:field', None)
        if not field:
            field = []
            fields['fixr:field'] = field
        return field

    def messages(self) -> list:
        """
        :return: a list of messages of an Orchestra instance
        """
        messages = self.obj.get('fixr:messages', None)
        if not messages:
            messages = {}
            self.obj['fixr:messages'] = messages
        message = messages.get('fixr:message', None)
        if not message:
            message = []
            messages['fixr:message'] = message
        return message

    @staticmethod
    def structure(message: dict) -> dict:
        structure = message.get('fixr:structure', None)
        if not structure:
            structure = {}
            message['fixr:structure'] = structure
        return structure

    @staticmethod
    def field_refs(structure: dict) -> list:
        field_refs = structure.get('fixr:fieldRef', None)
        if not field_refs:
            field_refs = []
            structure['fixr:fieldRef'] = field_refs
        return field_refs

    @staticmethod
    def component_refs(structure: dict) -> list:
        component_refs = structure.get('fixr:fieldRef', None)
        if not component_refs:
            component_refs = []
            structure['fixr:fieldRef'] = component_refs
        return component_refs

    @staticmethod
    def group_refs(structure: dict) -> list:
        groups_refs = structure.get('fixr:fieldRef', None)
        if not groups_refs:
            groups_refs = []
            structure['fixr:fieldRef'] = groups_refs
        return groups_refs

    def field(self, id: int) -> Union[dict, None]:
        fields: list = self.fields()
        return next((field for field in fields if field['@id'] == id), None)


OrchestraInstance = OrchestraInstance10
"""Default Orchestra instance"""
