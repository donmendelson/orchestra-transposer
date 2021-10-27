from pprint import pformat


class OrchestraInstance10:
    """
    An instance of Orchestra version 1.0
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else {}

    def __str__(self):
        return pformat(self.obj)

    def root(self) -> dict:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def metadata(self) -> dict:
        """
        :return: the metadata section of an Orchestra instance containing Dublin Core Terms
        """
        return self.obj["fixr:metadata"]


OrchestraInstance = OrchestraInstance10
"""Default Orchestra instance"""
