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

    def datatypes(self) -> list:
        """
        :return: a list of  datatypes of an Orchestra instance
        """
        return self.obj["fixr:datatypes"]["fixr:datatype"]

    def codesets(self) -> list:
        """
        :return: a list of  codesets of an Orchestra instance
        """
        return self.obj["fixr:codeSets"]['fixr:codeSet']

    def messages(self) -> list:
        """
        :return: a list of messages of an Orchestra instance
        """
        return self.obj["fixr:messages"]['fixr:message']


OrchestraInstance = OrchestraInstance10
"""Default Orchestra instance"""
