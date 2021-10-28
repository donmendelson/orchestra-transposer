from pprint import pformat


class SBEInstance10:

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj)

    def root(self) -> dict:
        return self.obj

    def all_types(self) -> list:
        all_types = self.obj.get('types', None)
        if all_types is None:
            all_types = []
            self.obj['types'] = all_types
        return all_types

    def encoding_types(self):
        return self.__types('type')

    def composites(self):
        return self.__types('composite')

    def enums(self):
        return self.__types('enum')

    def __types(self, category: str):
        all_types = self.all_types()

        for d in all_types:
            for key, val in d.items():
                if key == category:
                    return d

        d = {category: []}
        all_types.append(d)
        return d

    def append_encoding_type(self, encoding_type):
        types_d = self.encoding_types()
        types_l = list(types_d.values())[0]
        types_l.append(encoding_type)

    def append_enum(self, enum):
        types_d = self.enums()
        types_l = list(types_d.values())[0]
        types_l.append(enum)

    def messages(self) -> list:
        messages = self.obj.get('sbe:message', None)
        if messages is None:
            messages = []
            self.obj['sbe:message'] = messages
        return messages

    def append_message(self, message):
        self.messages().append(message)


SBEInstance = SBEInstance10
"""Default SBE instance"""
