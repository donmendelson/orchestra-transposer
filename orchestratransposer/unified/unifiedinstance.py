from pprint import pformat
from typing import Optional

TEXT_KEY = '$'
""" Symbol used by XMLSchema package for text content of an element (#text) """


class UnifiedInstanceNoPhrases:
    """
    An instance of Unified Repository 2010 Edition
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> dict:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def fix(self, version=None) -> Optional[dict]:
        """
        Returns a dictionary representing a fix version
        :param version: a fix version to extract from a Unified Repository. If not provided, returns the first instance.
        :return: a dictionary, or None if not found
        """
        try:
            root = self.root()
            if version:
                return next(fix for fix in root['fix'] if fix['@version'] == version)
            else:
                return root['fix'][0]
        except LookupError:
            return None


class UnifiedPhrasesInstance:
    """
    An instance of Unified Repository 2010 Edition Phrases file
    """

    def __init__(self, phrases_obj=None):
        self.phrases_obj = phrases_obj if phrases_obj is not None else {}

    def __str__(self):
        return pformat(self.phrases_obj, width=120)

    def phrases_root(self) -> dict:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.phrases_obj


class UnifiedInstanceWithPhrases(UnifiedInstanceNoPhrases):
    """
    An instance of Unified Repository 2010 Edition with its phrases
    """

    def __init__(self, obj=None, phrases_obj=None):
        super().__init__(obj)
        self.phrases = UnifiedPhrasesInstance(phrases_obj)

    def __str__(self):
        """ TODO not working - append phrases """
        return super().__str__()

    def phrases(self):
        return self.phrases


UnifiedInstance = UnifiedInstanceWithPhrases
"""Default Unified Repository instance"""
