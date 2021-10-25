import logging
from typing import List

from pysbeorchestra import Orchestra, OrchestraInstance, SBE, SBEInstance


class SBEOrchestraTranslator:
    """
    Translates between a Simple Binary Encoding message schema and an FIX Orchestra file.
    """

    def __init__(self):
        self.logger = logging.getLogger('SBEOrchestraTranslator')
        self.orchestra = Orchestra()
        self.sbe = SBE()

    def orchestra2sbe(self, orchestra_xml, sbe_stream) -> List[ValueError]:
        (data, errors) = self.orchestra.to_instance(orchestra_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orchestra_dict = data[0]
            sbe_instance = self.orchestra_dict2sbe_dict(orchestra_dict)
            self.sbe.write_instance(sbe_instance, sbe_stream)

    def orchestra_dict2sbe_dict(self, orch: OrchestraInstance) -> SBEInstance:
        sbe = SBEInstance()
        ms = sbe.root()
        repository = orch.root()
        ms["@package"] = repository["@name"]
        ms["@id"] = 1
        ms["@version"] = 0
        return sbe
