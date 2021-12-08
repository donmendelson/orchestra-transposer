from pprint import pformat
from typing import List, Optional, Tuple

TEXT_KEY = '$'
""" Symbol used by XMLSchema package for text content of an element (#text) """


class UnifiedMainInstance:
    """
    An instance of Unified Repository 2010 Edition
    """

    def __init__(self, obj: Optional[dict] = None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> dict:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def fix(self, version: Optional[str] = None) -> Optional[list]:
        """
        Returns a dictionary representing a fix version
        :param version: a fix version to extract from a Unified Repository. If not provided, returns the first instance.
        :return: a dictionary, or None if not found
        """
        try:
            main_root = self.root()
            if version:
                for i in main_root:
                    if isinstance(i, list) and i[0] == 'fix':
                        if isinstance(i[1], dict):
                            v = i[1].get('version', None)
                            if version == v:
                                return i
                return None
            else:
                for i in main_root:
                    if isinstance(i, list) and i[0] == 'fix':
                        return i
                return None
        except LookupError:
            return None

    @staticmethod
    def __types(fix: list, category: str) -> list:
        try:
            types = next(i for i in fix if isinstance(i, list) and i[0] == category)
        except StopIteration:
            types = [category]
            fix.append(types)
        return types

    @staticmethod
    def datatypes(fix: list) -> list:
        """
        :return: a list of  datatypes of a fix version of UnifiedInstance
        """
        return UnifiedMainInstance.__types(fix, 'datatypes')

    @staticmethod
    def fields(fix: list) -> list:
        """
        :return: a list of  fields of a fix version of UnifiedInstance
        """
        return UnifiedMainInstance.__types(fix, 'fields')

    @staticmethod
    def field(fix: list, field_id: int) -> Optional[list]:
        fields = UnifiedMainInstance.fields(fix)
        return next((field for field in fields if isinstance(field, list) and field[1]['id'] == field_id), None)

    @staticmethod
    def components(fix: list) -> list:
        """
        :return: a list of components and repeating groups of a fix version of UnifiedInstance
        """
        return UnifiedMainInstance.__types(fix, 'components')

    @staticmethod
    def messages(fix: list) -> list:
        """
        :return: a list of components and repeating groups of a fix version of UnifiedInstance
        """
        return UnifiedMainInstance.__types(fix, 'messages')

    @staticmethod
    def sections(fix: list) -> list:
        """
        :return: a list of sections of a fix version of UnifiedInstance
        """
        return UnifiedMainInstance.__types(fix, 'sections')

    @staticmethod
    def categories(fix: list) -> list:
        """
        :return: a list of categories of a fix version of UnifiedInstance
        """
        return UnifiedMainInstance.__types(fix, 'categories')

    @staticmethod
    def field(fix: list, field_id: int) -> Optional[list]:
        fields: list = UnifiedMainInstance.fields(fix)
        return next((field for field in fields if isinstance(field, list) and field[1]['id'] == field_id), None)

    @staticmethod
    def component(fix: list, component_id: int) -> Optional[list]:
        components: list = UnifiedMainInstance.components(fix)
        return next((component for component in components if
                     isinstance(component, list) and component[1]['id'] == component_id), None)


class UnifiedPhrasesInstance:
    """
    An instance of Unified Repository 2010 Edition Phrases file
    """

    def __init__(self, phrases_obj: Optional[dict] = None):
        self.phrases_obj = phrases_obj if phrases_obj is not None else {}

    def __str__(self):
        return pformat(self.phrases_obj, width=120)

    def phrases_root(self) -> dict:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.phrases_obj

    def text_id(self, text_id: str) -> List[Tuple[str, str]]:
        phrase = self.phrases_obj['phrase']
        if not phrase:
            phrase = []
            self.phrases_obj['phrase'] = phrase
        text = list(d['text'] for d in phrase if d['@textId'] == text_id)[0]
        return [(i['@purpose'], i['para'][0]) for i in text]


class UnifiedInstanceWithPhrases(UnifiedMainInstance):
    """
    An instance of Unified Repository 2010 Edition with its phrases
    """
    def __init__(self, unified: Optional[UnifiedMainInstance] = None, phrases: Optional[UnifiedPhrasesInstance] = None):
        super().__init__(unified.root() if unified is not None else None)
        self.phrases = phrases if phrases is not None else UnifiedPhrasesInstance()

    def __str__(self):
        return super.__str__(self) + str(self.phrases)

    def phrases(self):
        return self.phrases


UnifiedInstance = UnifiedInstanceWithPhrases
"""Default Unified Repository instance"""
