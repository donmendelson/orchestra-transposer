from pprint import pformat


class SBEInstance10:
    """
    Represents a message schema as defined by Simple Binary Encoding (SBE) version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> dict:
        """ Returns the data dictionary of this SBE instance """
        return self.obj

    def all_types(self) -> list:
        """
        Returns a List of all types

        TODO: If an input SBE file has types spread across multiple instances of types element, merge them into
        one dictionary.
        """
        all_types = self.obj.get('types', None)
        if all_types is None:
            all_types = []
            self.obj['types'] = all_types
        return all_types

    def first_types(self) -> dict:
        """ Returns the first instance of types, suitable for appending new encoding types """
        all_types = self.all_types()
        if len(all_types) == 0:
            all_types.append({})
        return all_types[0]

    def encoding_types(self) -> list:
        """ Returns simple encoding types"""
        return self.__types('type')

    def composites(self) -> list:
        """ Returns composite encoding types """
        return self.__types('composite')

    def enums(self) -> list:
        """ Returns enumerations, aka code sets """
        return self.__types('enum')

    def __types(self, category: str) -> list:
        first_types = self.first_types()

        for key, val in first_types.items():
            if key == category:
                return val
        l = []
        first_types[category] = l
        return l

    def append_encoding_type(self, encoding_type):
        """ Appends a simple encoding type """
        types_l = self.encoding_types()
        types_l.append(encoding_type)

    def append_composite(self, composite):
        """ Appends a composite type """
        types_l = self.composites()
        types_l.append(composite)

    def append_enum(self, enum):
        """ Appends an enumeration, aka code set """
        types_l = self.enums()
        types_l.append(enum)

    def composite(self, composite):
        """ Appends a composite type """
        types_l = self.composites()
        types_l.append(composite)

    def messages(self) -> list:
        """ Accesses A List of messages"""
        messages = self.obj.get('sbe:message', None)
        if messages is None:
            messages = []
            self.obj['sbe:message'] = messages
        return messages

    def append_message(self, message):
        """ Appends a message """
        self.messages().append(message)

    @staticmethod
    def append_field(structure: dict, field):
        """
        Append a fixed-length field to a message or group structure
        """
        fields = SBEInstance10.fields(structure)
        fields.append(field)

    @staticmethod
    def append_data_field(structure: dict, field):
        """
        Append a variable-length data field to a message or group structure
        """
        data = SBEInstance10.data(structure)
        data.append(field)

    @staticmethod
    def append_group(structure: dict, group):
        """
        Append a repeating group to a message or group structure
        """
        groups = SBEInstance10.groups(structure)
        groups.append(group)

    @staticmethod
    def fields(structure: dict) -> list:
        """
        Access the fixed-length fields of a message or group structure

        Does not include the fields in nested groups.
        """
        fields = structure.get('field', None)
        if not fields:
            fields = []
            structure['field'] = fields
        return fields

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
        all_sbe_fields.extend(fields)
        groups = SBEInstance10.groups(structure)
        for group in groups:
            SBEInstance10.all_data(group, all_sbe_fields)

    @staticmethod
    def data(structure: dict) -> list:
        """
        Access the variable-length data fields of a message or group structure

        Does not include data fields in nested groups.
        """
        data = structure.get('data', None)
        if not data:
            data = []
            structure['data'] = data
        return data

    @staticmethod
    def groups(structure: dict) -> list:
        """
        Access the repeating groups of a message or group structure
        """
        groups = structure.get('group', None)
        if not groups:
            groups = []
            structure['group'] = groups
        return groups

    @staticmethod
    def id(structure: dict) -> int:
        return structure.get('@id')


SBEInstance = SBEInstance10
"""Default SBE instance"""
