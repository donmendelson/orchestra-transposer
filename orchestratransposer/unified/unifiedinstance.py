from pprint import pformat
from typing import List, Optional, Tuple


class UnifiedMainInstance:
    """
    An instance of Unified Repository 2010 Edition
    """

    def __init__(self, obj: Optional[list] = None):
        self.obj = obj if obj is not None else ['fixRepository', {'edition': 2010}]

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> list:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def fix(self, version: Optional[str] = None, has_components=True, has_fixml=True, ) -> Optional[list]:
        """
        Returns a dictionary representing a fix version
        :param version: a fix version to extract from a Unified Repository. If not provided, returns the first instance.
        :param has_components: are components supported
        :param has_fixml: is FIXML supported
        :return: a list describing one version of a protocol
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
                fix_attr = {'version': version, 'components': 1 if has_components else 0,
                            'fixml': 1 if has_fixml else 0,
                            'specUrl': 'https://www.fixtrading.org/online-specification/'}
                fix = ['fix', fix_attr]
                main_root.append(fix)
                return fix
            else:
                for i in main_root:
                    if isinstance(i, list) and i[0] == 'fix':
                        return i
                fix_attr = {'version': version, 'components': 1 if has_components else 0,
                            'fixml': 1 if has_fixml else 0}
                fix = ['fix', fix_attr]
                main_root.append(fix)
                return fix
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
    def field_length_field(fix: list, field_id: int) -> Optional[list]:
        """
        Finds a Length field associated to a data field
        :param fix: a FIX version in a Unified Repository
        :param field_id: tag of an associated data field
        :return: a Length field if found, or None
        """
        fields = UnifiedMainInstance.fields(fix)
        return next((field for field in fields if isinstance(field, list) and field[1].get('associatedDataTag', None) ==
                     field_id), None)

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
    def component(fix: list, component_id: int) -> Optional[list]:
        components: list = UnifiedMainInstance.components(fix)
        return next((component for component in components if
                     isinstance(component, list) and component[1]['id'] == component_id), None)


class UnifiedPhrasesInstance:
    """
    An instance of Unified Repository 2010 Edition Phrases file
    """

    def __init__(self, phrases_obj: Optional[dict] = None):
        self.phrases_obj = phrases_obj if phrases_obj is not None else ['phrases', {}]

    def __str__(self):
        return pformat(self.phrases_obj, width=120)

    def phrases_root(self) -> list:
        """
        :return: the root of an Orchestra instance represented as a Python list
        """
        return self.phrases_obj

    def append_documentation(self, text_id: str, documentations: List[Tuple[str, str]]):
        """
        Append or replace documentation by key
        :param text_id: key for documentation of an element
        :param documentations: a list of one or more tuples, each containing a purpose string and documentation text
        """
        phrase_attr = {'textId': text_id}
        phrase = ['phrase', phrase_attr]
        # sort by purpose
        documentations.sort(key=lambda d: self._purpose_sort(d))
        last_purpose = "X"
        for documentation in documentations:
            purpose = documentation[0] or ""
            if not purpose == last_purpose:
                if documentation[0]:
                    attr = {'purpose': documentation[0]}
                else:
                    attr = {}
                text = ['text', attr]
                phrase.append(text)
                last_purpose = purpose
            if documentation[1]:
                text.append(['para', documentation[1]])

        # if already exists, remove old values
        old_phrase = next((p for p in self.phrases_root() if isinstance(p, list) and len(p) >= 2
                           and p[1].get('textId', None) == text_id), None)
        if old_phrase:
            self.phrases_root().remove(old_phrase)
        self.phrases_root().append(phrase)

    @staticmethod
    def _purpose_sort(d):
        if not d:
            return 2
        if not d[0]:
            return 2
        elif 'SYNOPSIS' == d[0]:
            return 0
        else:
            return 1;

    def text_id(self, text_id: str) -> List[Tuple[str, List[str]]]:
        """
        Retrieve documentation by key
        :param text_id: key for documentation of an element
        :return: a list of one or more tuples, each containing a purpose string and list of documentation paragraphs, or
        an empty list if the key is not found
        """
        retv = []
        phrase = next((p for p in self.phrases_root() if isinstance(p, list) and len(p) >= 2
                       and p[1].get('textId', None) == text_id), None)
        if phrase:
            text = filter(lambda l: isinstance(l, list) and l[0] == 'text', phrase)
            for i in text:
                pd = next((p for p in i if isinstance(p, dict)), None)
                if pd:
                    purpose = pd.get('purpose', None)
                else:
                    purpose = None
                paras = list(filter(lambda l: isinstance(l, list) and l[0] == 'para', i))
                retv.append((purpose, list(map(lambda p: p[1], paras))))
        return retv


class UnifiedInstanceWithPhrases(UnifiedMainInstance):
    """
    An instance of Unified Repository 2010 Edition with its phrases
    """

    def __init__(self, unified: Optional[UnifiedMainInstance] = None, phrases: Optional[UnifiedPhrasesInstance] = None):
        super().__init__(unified.root() if unified is not None else UnifiedMainInstance().root())
        self.phrases = phrases if phrases is not None else UnifiedPhrasesInstance()

    def __str__(self):
        return pformat(self.obj, width=120) + str(self.phrases)

    def text_id(self, text_id: str) -> List[Tuple[str, List[str]]]:
        """
        Returns a list of documentation for an element, given a unique key

        Each element of the returned list is a tuple of purpose and list of documentation text. Purpose may be None.
        """
        return self.phrases.text_id(text_id)

    def append_documentation(self, text_id: str, text: List[Tuple[str, str]]) -> None:
        """
        Append or replace documentation by key
        :param text_id: key for documentation of an element
        :param text: a list of one or more tuples, each containing a purpose string and documentation text
        """
        self.phrases.append_documentation(text_id, text)


UnifiedInstance = UnifiedInstanceWithPhrases
"""Default Unified Repository instance"""
