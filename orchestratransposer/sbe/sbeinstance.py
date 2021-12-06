import itertools
from pprint import pformat


class SBEInstance10:
    """
    Represents a message schema as defined by Simple Binary Encoding (SBE) version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else ['sbe:messageSchema', {}]
        self._all_data = None

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> list:
        """ Returns the data dictionary of this SBE instance """
        return self.obj

    def message_schema(self) -> list:
        """ Returns attributes of a message schema """
        try:
            return next(i for i in self.root() if isinstance(i, dict))
        except StopIteration:
            d = {}
            self.obj.append(d)
            return d

    @property
    def all_types(self) -> list:
        """
        Returns a List of all types lists
        """
        if self._all_data is None:
            self._all_data = list(
                itertools.chain(filter(lambda l: isinstance(l, list) and l[0] == 'types', self.root())))
        return self._all_data

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

            {'@length': 1,
            '@name': 'timestampEncoding',
            '@primitiveType': 'uint64',
            '@semanticType': 'UTCTimestamp',
            '@sinceVersion': 0}
        """
        types_l = self.first_types()
        types_l.append(['type', encoding_type])

    def append_composite(self, composite):
        """
        Appends a composite type

        .. code-block:: python

            {'@name': 'MONTH_YEAR',
           '@semanticType': 'MonthYear',
           'type': [{'@length': 1,
                     '@name': 'year',
                     '@presence': 'required',
                     '@primitiveType': 'uint16'},
                    {'@length': 1,
                     '@name': 'month',
                     '@presence': 'required',
                     '@primitiveType': 'uint8'},
                    {'@length': 1,
                     '@name': 'day',
                     '@presence': 'required',
                     '@primitiveType': 'uint8'},
                    {'@length': 1,
                     '@name': 'week',
                     '@presence': 'required',
                     '@primitiveType': 'uint8']}
        """
        types_l = self.first_types()
        types_l.append(['composite', composite])

    def append_enum(self, enum):
        """
        Appends an enumeration, aka code set

        An enum should have the attributes as shown below.

        Note that all simple attributes start with '@' character. The value of a code in the enumeration has
        a key of '$'. That special symbol causes a translation to XML element text rather than an XML named attribute.

        .. code-block:: python

            {'@encodingType': 'enumEncoding',
            '@name': 'sideEnum',
            'validValue': [{'$': '1', '@name': 'Buy', '@sinceVersion': 0},
                           {'$': '2', '@name': 'Sell', '@sinceVersion': 0}]}
        """
        types_l = self.first_types()
        types_l.append(['enum', enum])

    def encoding_types(self):
        """ Access simple encoding types """
        types_l = self.first_types()
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'type', types_l))

    def composites(self):
        """ Access composite types """
        types_l = self.first_types()
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'composite', types_l))

    def enums(self):
        """ Access enums """
        types_l = self.first_types()
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'enum', types_l))

    def messages(self) -> list:
        """ Accesses a List of messages"""
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'sbe:message', self.root()))

    def append_message(self, message):
        """
        Appends a message

        A message should have the attributes as shown below.

        .. code-block:: python

            {'@text_id': 97,
            '@name': 'BusinessMessageReject',
            '@semanticType': 'j',
            'data': [{'@text_id': 58,
                    '@name': 'Text',
                    '@presence': 'required',
                    '@semanticType': 'data',
                    '@type': 'DATA'},
            'field': [{@text_id': 379,
                     '@name': 'BusinesRejectRefId',
                     '@presence': 'required',
                     '@semanticType': 'String',
                     '@type': 'idString'},
                    {'@text_id': 380,
                     '@name': 'BusinessRejectReason',
                     '@offset': 8,
                     '@presence': 'required',
                     '@type': 'businessRejectReasonEnum'}]}
        """
        self.root().append(message)

    @staticmethod
    def append_field(structure: list, field):
        """
        Append a fixed-length field to a message or group structure as the last fixed-length field

        A field should have the attributes as shown below.

        .. code-block:: python

            {'@text_id': 37,
             '@name': 'OrderID',
             '@presence': 'required',
             '@semanticType': 'String',
             '@type': 'idString'}
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
