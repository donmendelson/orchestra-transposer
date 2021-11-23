from pprint import pformat

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


class UnifiedInstanceWithPhrases(UnifiedInstanceNoPhrases, UnifiedPhrasesInstance):
    """
    An instance of Unified Repository 2010 Edition with its phrases
    """

    def __init__(self, obj=None, phrases_obj=None):
        super().__init__(obj)
        self.phrases_obj = phrases_obj if phrases_obj is not None else {}

    def __str__(self):
        return pformat(self.root(), width=120) + pformat(self.phrases_root(), width=120)


UnifiedInstance = UnifiedInstanceWithPhrases
"""Default Unified Repository instance"""
