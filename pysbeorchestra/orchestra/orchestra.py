import xml.etree.ElementTree as ET
import os
import xmlschema


class Orchestra:
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema.
    """
    SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), 'schemas/')

    def __init__(self):
        xsd_path = os.path.join(self.SCHEMAS_DIR, 'v1-0/repository.xsd')
        self.xsd = xmlschema.XMLSchema(xsd_path)

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
        ET.register_namespace('fixr','http://fixprotocol.io/2020/orchestra/repository')
        ET.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        stream.write(ET.tostring(et[0], encoding='utf8', method='xml'))
