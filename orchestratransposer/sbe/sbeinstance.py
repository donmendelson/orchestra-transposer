from pprint import pformat


class SBEInstance10:
    """
    Represents a message schema as defined by Simple Binary Encoding (SBE) version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj)

    def root(self) -> dict:
        """ Returns the data dictionary of this SBE instance """
        return self.obj

    def all_types(self) -> list:
        """ Returns a List of all types """
        all_types = self.obj.get('types', None)
        if all_types is None:
            all_types = []
            self.obj['types'] = all_types
        return all_types

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
        all_types = self.all_types()

        for d in all_types:
            for key, val in d.items():
                if key == category:
                    return val
        l = []
        d = {category: l}
        all_types.append(d)
        return l

    def append_encoding_type(self, encoding_type):
        """ Appends a simple encoding type """
        types_l = self.encoding_types()
        types_l.append(encoding_type)

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
        fields = SBEInstance.fields(structure)
        fields.append(field)

    @staticmethod
    def append_data_field(structure: dict, field):
        """
        Append a variable-length data field to a message or group structure
        """
        data = SBEInstance.data(structure)
        data.append(field)

    @staticmethod
    def append_group(structure: dict, group):
        """
        Append a repeating group to a message or group structure
        """
        groups = SBEInstance.groups(structure)
        groups.append(group)

    @staticmethod
    def fields(structure: dict) -> list:
        """
        Access the fixed-length fields of a message or group structure
        """
        fields = structure.get('field', None)
        if not fields:
            fields = []
            structure['field'] = fields
        return fields

    @staticmethod
    def data(structure: dict) -> list:
        """
        Access the variable-length data fields of a message or group structure
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


SBEInstance = SBEInstance10
"""Default SBE instance"""
