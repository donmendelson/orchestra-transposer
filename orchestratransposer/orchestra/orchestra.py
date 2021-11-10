import os
from typing import Iterator, List, Tuple
from xml.etree import ElementTree

from xmlschema import XMLSchema

from .orchestrainstance import OrchestraInstance10
from ..sbe.sbe import SBE10


class Orchestra10:
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema.
    """

    def __init__(self):
        self.xsd = XMLSchema(Orchestra10.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas/')
        return os.path.join(schemas_dir, 'v1-0/repository.xsd')

    def validate(self, xml) -> Iterator[Exception]:
        """
        Validates an XML data against the XSD schema/component instance. Creates an iterator for the errors generated
        by the validation of an XML data against the XSD schema/component instance.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        return self.xsd.iter_errors(xml)

    def read_xml(self, xml) -> Tuple[OrchestraInstance10, List[Exception]]:
        """
        Creates an OrchestraInstance and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        data, errors = [], []
        for result in self.xsd.iter_decode(xml):
            if not isinstance(result, Exception):
                data.append(result)
            else:
                errors.append(result)
        return OrchestraInstance10(data[0]), errors

    def write_xml(self, instance: OrchestraInstance10, stream) -> List[Exception]:
        """
        Encodes an OrchestraInstance and writes it to a stream.

        :param instance: an OrchestraInstance dictionary
        :param stream: a file like object
        :return: a list of errors, if any
        """
        data, errors = self.xsd.encode(instance.root(), validation='lax', use_defaults=False,
                                       namespaces={'fixr': 'http://fixprotocol.io/2020/orchestra/repository',
                                                   'dcterms': 'http://purl.org/dc/terms/',
                                                   'dc': 'http://purl.org/dc/elements/1.1/'})
        ElementTree.register_namespace(
            'fixr', 'http://fixprotocol.io/2020/orchestra/repository')
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        stream.write(ElementTree.tostring(data, encoding='utf8', method='xml'))
        return errors


class Orchestra10WithSBETypes(Orchestra10):
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema Supports SBE snippets in mappedDatatype.
    """

    def __init__(self):
        orch_xsd_path = Orchestra10.get_xsd_path()
        sbe_xsd_path = SBE10.get_xsd_path()
        self.xsd = XMLSchema([orch_xsd_path, sbe_xsd_path])

    def write_xml(self, instance: OrchestraInstance10, stream) -> List[Exception]:
        """
        Encodes an OrchestraInstance and writes it to a stream.

        :param instance: an OrchestraInstance dictionary
        :param stream: a file like object
        """
        data, errors = self.xsd.encode(instance.root(), validation='lax', use_defaults=False,
                                       namespaces={'fixr': 'http://fixprotocol.io/2020/orchestra/repository',
                                                   'dcterms': 'http://purl.org/dc/terms/',
                                                   'dc': 'http://purl.org/dc/elements/1.1/',
                                                   'sbe': 'http://fixprotocol.io/2016/sbe'})
        ElementTree.register_namespace(
            'fixr', 'http://fixprotocol.io/2020/orchestra/repository')
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        ElementTree.register_namespace('sbe', "http://fixprotocol.io/2016/sbe")
        stream.write(ElementTree.tostring(data, encoding='utf8', method='xml'))
        return errors


Orchestra = Orchestra10WithSBETypes
""" Default Orchestra schema implementation """
