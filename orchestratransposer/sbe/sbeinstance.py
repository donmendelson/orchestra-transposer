from pprint import pformat
from typing import Optional


class SBEInstance10:
    """
    Represents a message schema as defined by Simple Binary Encoding (SBE) version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else ['sbe:messageSchema', {}]
        self._all_encoding_types = None

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> list:
        """ Returns the data dictionary of this SBE instance """
        return self.obj

    def message_schema(self) -> dict:
        """ Returns attributes of a message schema """
        try:
            return next(i for i in self.root() if isinstance(i, dict))
        except StopIteration:
            d = {}
            self.obj.append(d)
            return d

    def all_types(self) -> list:
        """
        Returns a List of all types lists
        """
        if self._all_encoding_types is None:
            self._all_encoding_types = []
            for i in filter(lambda l: isinstance(l, list) and l[0] == 'types', self.root()):
                for j in filter(lambda l: isinstance(l, list), i):
                    self._all_encoding_types.append(list(j))
        return self._all_encoding_types

    def first_types(self) -> list:
        """ Returns the first instance of types list, suitable for appending new encoding types """
        try:
            return next(l for l in self.root() if isinstance(l, list) and l[0] == 'types')
        except StopIteration:
            types = ['types']
            self.root().append(types)
            return types

    def append_encoding_type(self, encoding_type):
        """
        Appends a simple encoding type

        .. code-block:: python

           ['type', {'name': 'date', 'primitiveType': 'uint16', 'semanticType': 'LocalMktDate'}]

        """
        types_l = self.first_types()
        types_l.append(encoding_type)

    def append_composite(self, composite):
        """
        Appends a composite type

        .. code-block:: python

        ['composite',
           {'name': 'MONTH_YEAR', 'semanticType': 'MonthYear'},
           ['type', {'name': 'year', 'primitiveType': 'uint16'}],
           ['type', {'name': 'month', 'primitiveType': 'uint8'}],
           ['type', {'name': 'day', 'primitiveType': 'uint8'}],
           ['type', {'name': 'week', 'primitiveType': 'uint8'}]]
        """
        types_l = self.first_types()
        types_l.append(composite)

    def append_enum(self, enum):
        """
        Appends an enumeration, aka code set

        An enum should have the attributes as shown below.

        .. code-block:: python

          ['enum',
           {'encodingType': 'enumEncoding', 'name': 'sideEnum'},
           ['validValue', {'name': 'Buy'}, '1'],
           ['validValue', {'name': 'Sell'}, '2']]]
        """
        types_l = self.first_types()
        types_l.append(enum)

    def encoding_types(self) -> list:
        """ Access simple encoding types """
        types_l = self.all_types()
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'type', types_l))

    def composites(self) -> list:
        """ Access composite types """
        types_l = self.all_types()
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'composite', types_l))

    def composite_by_name(self, composite_name: str) -> Optional[list]:
        composites = self.composites()
        return next((composite for composite in composites if
                     isinstance(composite, list) and composite[1]['name'].casefold() == composite_name.casefold()),
                    None)

    def enums(self) -> list:
        """ Access enums """
        types_l = self.all_types()
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'enum', types_l))

    def messages(self) -> list:
        """ Accesses a List of messages"""
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'sbe:message', self.root()))

    def append_message(self, message):
        """
        Appends a message

        A message should have the attributes as shown below.

        .. code-block:: python

         ['sbe:message',
          {'blockLength': 9, 'id': 97, 'name': 'BusinessMessageReject', 'semanticType': 'j'},
          ['field', {'id': 379, 'name': 'BusinesRejectRefId', 'offset': 0, 'semanticType': 'String', 'type': 'idString'}],
          ['field',
           {'id': 380, 'name': 'BusinessRejectReason', 'offset': 8, 'semanticType': 'int', 'type': 'businessRejectReasonEnum'}],
          ['data', {'id': 58, 'name': 'Text', 'semanticType': 'data', 'type': 'DATA'}]]
        """
        self.root().append(message)

    @staticmethod
    def append_field(structure: list, field):
        """
        Append a fixed-length field to a message or group structure as the last fixed-length field

        A field should have the attributes as shown below.

        .. code-block:: python

            ['field', {'id': 54, 'name': 'Side', 'offset': 24, 'semanticType': 'char', 'type': 'sideEnum'}]
        """
        try:
            pos = next(i for i in reversed(range(len(structure))) if isinstance(structure[i], list) and
                       structure[i][0] == 'field')
            structure.insert(pos + 1, field)
        except StopIteration:
            structure.append(field)

    @staticmethod
    def append_data_field(structure: list, field):
        """
        Append a variable-length data field to a message or group structure as the last group

        Attributes for a variable-length field are the same as for fixed length, but the field is inserted into a
        different part of a message structure.
        """
        structure.append(field)

    @staticmethod
    def append_group(structure: list, group):
        """
        Append a repeating group to a message or group structure
        """
        try:
            pos = next(i for i in reversed(range(len(structure))) if isinstance(structure[i], list) and
                       structure[i][0] == 'group')
            structure.insert(pos + 1, group)
        except StopIteration:
            structure.append(group)

    @staticmethod
    def fields(structure: dict) -> list:
        """
        Access the fixed-length fields of a message or group structure

        Does not include the fields in nested groups.
        """
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'field', structure))

    def field_by_name(self, structure: dict, field_name: str) -> Optional[list]:
        """
        Find a field by name in a message structure
        :param structure: a message
        :param field_name: name of field to find
        :return: a field, or None if not found
        """
        all_sbe_fields: list = []
        self.all_fields(structure, all_sbe_fields)
        return next((field for field in all_sbe_fields if
                     isinstance(field, list) and field[1]['name'].casefold() == field_name.casefold()),
                    None)

    def field_by_type(self, structure: dict, field_type: str) -> Optional[list]:
        """
        Find a field by type in a message structure
        :param structure: a message
        :param field_type: type of field to find
        :return: a field, or None if not found
        """
        all_sbe_fields: list = []
        self.all_fields(structure, all_sbe_fields)
        return next((field for field in all_sbe_fields if
                     isinstance(field, list) and field[1]['type'].casefold() == field_type.casefold()),
                    None)

    def first_field_by_type(self, field_name: str) -> Optional[list]:
        """
        Returns the first field of any message that has the given type
        :param field_name: name to match
        :return: a field, or None if no match
        """
        messages = self.messages()
        for message in messages:
            field = self.field_by_type(message, field_name)
            if field:
                return field
        return None

    @staticmethod
    def all_fields(structure: dict, all_sbe_fields: list):
        """
        Access the fixed-length fields of a message or group structure

        Recursively gathers the fields in nested groups.
        :param structure: message or group structure
        :param all_sbe_fields: list of fields to populate
        :return:
        """
        fields = SBEInstance10.fields(structure)
        all_sbe_fields.extend(fields)
        groups = SBEInstance10.groups(structure)
        if groups:
            for group in groups:
                SBEInstance10.all_fields(group, all_sbe_fields)

    @staticmethod
    def all_data(structure: dict, all_sbe_fields: list):
        """
        Access the variable-length fields of a message or group structure

        Recursively gathers the fields in nested groups.
        :param structure: message or group structure
        :param all_sbe_fields: list of fields to populate
        :return:
        """
        fields = SBEInstance10.data(structure)
        if fields:
            all_sbe_fields.extend(fields)
        groups = SBEInstance10.groups(structure)
        if groups:
            for group in groups:
                SBEInstance10.all_data(group, all_sbe_fields)

    @staticmethod
    def data(structure: dict) -> list:
        """
        Access the variable-length data fields of a message or group structure

        Does not include data fields in nested groups.
        """
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'data', structure))

    @staticmethod
    def groups(structure: dict) -> list:
        """
        Access the repeating groups of a message or group structure
        """
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'group', structure))

    @staticmethod
    def id(structure: list) -> int:
        return structure[1].get('id')


SBEInstance = SBEInstance10
"""Default SBE instance"""


class SBEInstance20(SBEInstance10):
    """
    Represents a message schema as defined by Simple Binary Encoding (SBE) version 2.0 release candidate
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else ['messageSchema', {}]
        self._all_encoding_types = None
        self._all_messages = None

    def first_messages(self) -> list:
        """ Returns the first instance of message list, suitable for appending new messages """
        try:
            return next(l for l in self.root() if isinstance(l, list) and l[0] == 'messages')
        except StopIteration:
            messages = ['messages']
            self.root().append(messages)
            return messages

    def messages(self) -> list:
        """ Accesses a combined List of messages"""
        if self._all_messages is None:
            self._all_messages = []
            for i in filter(lambda l: isinstance(l, list) and l[0] == 'messages', self.root()):
                for j in filter(lambda l: isinstance(l, list), i):
                    self._all_messages.append(list(j))
        return self._all_messages

    def append_message(self, message):
        """
        Appends a message
        """
        self.first_messages().append(message)
