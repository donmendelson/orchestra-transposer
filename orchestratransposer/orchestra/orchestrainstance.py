from pprint import pformat
from typing import List, Optional, Tuple


class OrchestraInstance10:
    """
    An instance of Orchestra version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else ['fixr:repository', {}]

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> list:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def repository(self) -> dict:
        """ Returns attributes of a repository """
        try:
            return next(i for i in self.obj if isinstance(i, dict))
        except StopIteration:
            d = {}
            self.obj.append(d)
            return d

    def metadata(self) -> list:
        """
        :return: the metadata section of an Orchestra instance containing Dublin Core Terms
        """
        try:
            metadata = next(l for l in self.root() if isinstance(l, list) and l[0] == 'fixr:metadata')
        except StopIteration:
            metadata = ['fixr:metadata']
            self.root().append(metadata)
        return metadata

    def __types(self, category: str) -> list:
        try:
            types = next(i for i in self.root() if isinstance(i, list) and i[0] == category)
        except StopIteration:
            types = [category]
            self.root().append(types)
        return types

    def datatypes(self) -> list:
        """
        :return: a list of  datatypes of an Orchestra instance
        """
        return self.__types('fixr:datatypes')

    def codesets(self) -> list:
        """
        :return: a list of  codesets of an Orchestra instance
        """
        return self.__types('fixr:codeSets')

    def fields(self) -> list:
        """
        :return: a list of  fields of an Orchestra instance
        """
        return self.__types('fixr:fields')

    def components(self) -> list:
        """
        :return: a list of  components of an Orchestra instance
        """
        return self.__types('fixr:components')

    def groups(self) -> list:
        """
        :return: a list of  components of an Orchestra instance
        """
        return self.__types('fixr:groups')

    def messages(self) -> list:
        """
        :return: a list of messages of an Orchestra instance
        """
        return self.__types('fixr:messages')

    def append_message(self, message: dict):
        """
        Add a message to this Orchestra instance

        :param message: a message is represented as a dictionary in the following format.

        Note that all simple attributes start with '@' character.

        .. code-block:: python

       'fixr:message': [{
             '@text_id': 1,
             '@msgType': '0',
             '@name': 'Heartbeat',
             '@scenario': 'base',
             'fixr:annotation': {
                     'fixr:documentation': [{'$': 'The Heartbeat monitors the '
                                                  'status of the communication '
                                                  'link and identifies when the '
                                                  'last of a string of messages '
                                                  'was not received.',
                                             '@contentType': 'text/plain',
                                             '@purpose': 'SYNOPSIS'}]},
                        'fixr:structure': {
                            'fixr:componentRef': [{'@text_id': 1024,
                               '@presence': 'required',
                               '@scenario': 'base',}                                                                                                                         '@supported': 'supported'}]}},
                                {'@text_id': 1025,
                               '@presence': 'required',
                               '@scenario': 'base'}],
                            'fixr:fieldRef': [{
                               '@text_id': 112,
                               '@presence': 'optional',
                               '@scenario': 'base'}]]
        """
        messages = self.messages()
        messages.append(message)

    def append_group(self, group: dict):
        """
    Add a repeating group to this Orchestra instance

    :param group: a group is represented as a dictionary

    Note that all simple attributes start with '@' character.
     """
        groups = self.groups()
        groups.append(group)

    @staticmethod
    def structure(message: list) -> list:
        try:
            return next(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:structure', message))
        except StopIteration:
            struct = ['fixr:structure']
            message.append(struct)
        return struct

    @staticmethod
    def documentation(element: list) -> List[Tuple[str, str]]:
        """ Returns a list of documentation elements, each a tuple of purpose (possibly None) and text """
        try:
            annotation = next(i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation')
            documentation = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:documentation', annotation)
            return list(map(OrchestraInstance10.__map_documentation, documentation))
        except StopIteration:
            return []

    @staticmethod
    def __map_documentation(element: list) -> Tuple[str, str]:
        try:
            attr = next(i for i in element if isinstance(i, dict))
            purpose = attr['purpose']
        except StopIteration:
            purpose = None
        try:
            text = element[2]
        except IndexError:
            text = None
        return purpose, text

    @staticmethod
    def append_documentation(element: dict, documentation: str):
        annotation = element.get('fixr:annotation', None)
        if not annotation:
            annotation = {}
            element['fixr:annotation'] = annotation
        documentations = annotation.get('fixr:documentation', None)
        if not documentations:
            documentations = []
            annotation['fixr:documentation'] = documentations
        documentations.append({'$': documentation})

    @staticmethod
    def field_refs(structure: list) -> list:
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:fieldRef', structure))

    @staticmethod
    def component_refs(structure: list) -> list:
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:componentRef', structure))

    @staticmethod
    def group_refs(structure: list) -> list:
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:groupRef', structure))

    def field(self, field_id: int) -> Optional[list]:
        fields: list = self.fields()
        return next((field for field in fields if isinstance(field, list) and field[1]['id'] == field_id), None)

    def component(self, component_id: int) -> Optional[list]:
        components: list = self.components()
        return next((component for component in components if
                     isinstance(component, list) and component[1]['id'] == component_id), None)

    def group(self, group_id: int) -> Optional[list]:
        groups: list = self.groups()
        return next((group for group in groups if isinstance(group, list) and group[1]['id'] == group_id), None)

    @staticmethod
    def append_field_ref(structure: list, field_ref):
        """
        Append a fieldRef to a message or group structure
        """
        field_refs = OrchestraInstance10.field_refs(structure)
        field_refs.append(field_ref)

    @staticmethod
    def append_group_ref(structure: list, group_ref):
        """
        Append a groupRef to a message or group structure
        """
        group_refs = OrchestraInstance10.group_refs(structure)
        group_refs.append(group_ref)


OrchestraInstance = OrchestraInstance10
"""Default Orchestra instance"""
