import os
from typing import Iterator, List, Tuple
from xml.etree import ElementTree

from xmlschema import JsonMLConverter, XMLSchema

from .orchestrainstance import OrchestraInstance10
from ..sbe.sbe import SBE10, SBE20


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

    def validate(self, xml) -> List[Exception]:
        """
        Validates an XML data against the XSD schema/component instance. Creates an iterator for the errors generated
        by the validation of an XML data against the XSD schema/component instance.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        errors = []
        for result in self.xsd.iter_errors(xml):
            errors.append(result)
        return errors

    def read_xml(self, xml) -> Tuple[OrchestraInstance10, List[Exception]]:
        """
        Creates an OrchestraInstance and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        data, errors = [], []
        # counterintuitively, validation='skip' allows attributes from 'any' type to pass through
        for result in self.xsd.iter_decode(xml, use_defaults=False, validation='skip', converter=JsonMLConverter):
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
                                                   'dc': 'http://purl.org/dc/elements/1.1/'},
                                       **{'converter': JsonMLConverter})
        ElementTree.register_namespace(
            'fixr', 'http://fixprotocol.io/2020/orchestra/repository')
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        stream.write(ElementTree.tostring(data, encoding='utf-8', method='xml'))
        return errors


class FixmlAppinfo:
    """
    Represents the XML schema for appinfo elements imported into Orchestra
    """

    def __init__(self):
        self.xsd = XMLSchema(FixmlAppinfo.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas/appinfo/')
        return os.path.join(schemas_dir, 'FIXMLappinfo.xsd')


class Orchestra10WithAppinfo(Orchestra10):
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema with support for appinfo elements for FIXML.
    """

    def __init__(self):
        orch_xsd_path = Orchestra10WithAppinfo.get_xsd_path()
        fixml_xsd_path = FixmlAppinfo.get_xsd_path()
        self.xsd = XMLSchema([orch_xsd_path, fixml_xsd_path])

    def write_xml(self, instance: OrchestraInstance10, stream) -> List[Exception]:
        """
        Encodes an OrchestraInstance and writes it to a stream.

        :param instance: an OrchestraInstance dictionary
        :param stream: a file like object
        """
        # validation='skip' required to write appinfo attributes, so no errors returned
        data = self.xsd.encode(instance.root(), validation='skip', use_defaults=False,
                                       namespaces={'fixr': 'http://fixprotocol.io/2020/orchestra/repository',
                                                   'dcterms': 'http://purl.org/dc/terms/',
                                                   'dc': 'http://purl.org/dc/elements/1.1/',
                                                   'fixml': 'http://fixprotocol.io/2022/orchestra/appinfo/fixml'},
                                       **{'converter': JsonMLConverter})
        ElementTree.register_namespace(
            'fixr', 'http://fixprotocol.io/2020/orchestra/repository')
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        ElementTree.register_namespace('fixml', 'http://fixprotocol.io/2022/orchestra/appinfo/fixml')
        stream.write(ElementTree.tostring(data, encoding='utf-8', method='xml'))
        return []


class Orchestra10WithSBE10Types(Orchestra10):
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema Supports SBE snippets in mappedDatatype.
    """

    def __init__(self):
        orch_xsd_path = Orchestra10WithSBE10Types.get_xsd_path()
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
                                                   'sbe': 'http://fixprotocol.io/2016/sbe'},
                                       **{'converter': JsonMLConverter})
        ElementTree.register_namespace(
            'fixr', 'http://fixprotocol.io/2020/orchestra/repository')
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        ElementTree.register_namespace('sbe', "http://fixprotocol.io/2016/sbe")
        stream.write(ElementTree.tostring(data, encoding='utf-8', method='xml'))
        return errors


class Orchestra10WithSBE20Types(Orchestra10):
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema Supports SBE snippets in mappedDatatype.
    """

    def __init__(self):
        orch_xsd_path = Orchestra10WithSBE20Types.get_xsd_path()
        sbe_xsd_path = SBE20.get_xsd_path()
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
                                                   'sbe': 'http://fixprotocol.io/2017/sbe'},
                                       **{'converter': JsonMLConverter})
        ElementTree.register_namespace(
            'fixr', 'http://fixprotocol.io/2020/orchestra/repository')
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        ElementTree.register_namespace('sbe', "http://fixprotocol.io/2017/sbe")
        stream.write(ElementTree.tostring(data, encoding='utf-8', method='xml'))
        return errors


Orchestra = Orchestra10WithAppinfo
""" Default Orchestra schema implementation """

