import xml.etree.ElementTree as ET

import xmlschema


class SBE:
    """
    Represents the XML schema for Simple Binary Encoding version 1.0 and processing of XML instances \
    that conform to that schema.
    """

    def __init__(self):
        self.xsd = xmlschema.XMLSchema('pysbeorchestra/sbe/schema/sbe.xsd')

    def validate(self, xml) -> None:
        """
        Validates an XML data against the XSD schema/component instance.

        :param source: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        :raises: :exc:`XMLSchemaValidationError` if the XML data instance is invalid.
        """
        self.xsd.validate(xml)

    def to_dict(self, xml):
        """
        Decodes an XML source to a data structure.

        :param source: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        return self.xsd.decode(xml)

    def from_dict(self, obj, stream):
        """
        Encodes a data structure XML data and writes it to a stream.

        :param obj: a data structure in the form returned by :meth:`to_dict`
        :param stream: a file like object
        """
        et = self.xsd.encode(obj, validation='lax')
        ET.register_namespace('sbe',"http://fixprotocol.io/2016/sbe")
        stream.write(ET.tostring(et[0], encoding='utf8', method='xml'))
