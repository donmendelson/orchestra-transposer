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

        .. code-block:: python

        ['fixr:message',
           {'abbrName': 'Heartbeat', 'added': 'FIX.2.7', 'category': 'Session', 'id': 1, 'msgType': '0', 'name': 'Heartbeat'},
           ['fixr:structure',
            ['fixr:componentRef',
             {'added': 'FIX.2.7', 'id': 1024, 'presence': 'required'},
             ['fixr:annotation', ['fixr:documentation', 'MsgType = 0']]],
            ['fixr:fieldRef',
             {'added': 'FIX.4.0', 'id': 112},
             ['fixr:annotation',
              ['fixr:documentation', 'Required when the heartbeat is the result of a Test Request message.']]],
            ['fixr:componentRef',
             {'added': 'FIX.2.7', 'id': 1025, 'presence': 'required'},
             ['fixr:annotation', ['fixr:documentation']]]],
           ['fixr:annotation',
            ['fixr:documentation',
             {'purpose': 'SYNOPSIS'},
             'The Heartbeat monitors the status of the communication link and identifies when the last of a string of messages '
             'was not received.']]],
        """
        messages = self.messages()
        messages.append(message)

    def append_group(self, group: dict):
        """
        Add a repeating group to this Orchestra instance

        :param group: a group is represented as a dictionary

        .. code-block:: python
          ['fixr:group',
           {'abbrName': 'Stip', 'added': 'FIX.4.4', 'category': 'Common', 'id': 1007, 'name': 'LegStipulations'},
           ['fixr:numInGroup', {'id': 683}, ['fixr:annotation', ['fixr:documentation']]],
           ['fixr:fieldRef',
            {'added': 'FIX.4.4', 'id': 688},
            ['fixr:annotation', ['fixr:documentation', 'Required if NoLegStipulations >0']]],
           ['fixr:fieldRef', {'added': 'FIX.4.4', 'id': 689}, ['fixr:annotation', ['fixr:documentation']]],
           ['fixr:annotation',
            ['fixr:documentation',
             {'purpose': 'SYNOPSIS'},
             'The LegStipulations component block has the same usage as the Stipulations component block, but for a leg '
             'instrument in a multi-legged security.'],
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
    def append_documentation(element: list, documentation: str):
        annotation = next((i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation'), None)
        if not annotation:
            annotation = ['fixr:annotation']
            element.append(annotation)
        annotation.append(['fixr:documentation', {}, documentation])

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
        try:
            pos = next(i for i in reversed(range(len(structure))) if isinstance(structure[i], list) and
                       structure[i][0] == 'fixr:annotation')
            structure.insert(pos, field_ref)
        except StopIteration:
            structure.append(field_ref)

    @staticmethod
    def append_group_ref(structure: list, group_ref):
        """
        Append a groupRef to a message or group structure
        """
        try:
            pos = next(i for i in reversed(range(len(structure))) if isinstance(structure[i], list) and
                       structure[i][0] == 'fixr:annotation')
            structure.insert(pos, group_ref)
        except StopIteration:
            structure.append(group_ref)


OrchestraInstance = OrchestraInstance10
"""Default Orchestra instance"""
