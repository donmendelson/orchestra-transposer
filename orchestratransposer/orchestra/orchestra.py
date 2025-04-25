import os
from typing import List, Tuple
from xml.etree import ElementTree

from xmlschema import JsonMLConverter, XMLSchema

from .orchestrainstance import OrchestraInstance10, OrchestraInstance11

SCHEMAS_DIR = 'schemas'
"""Directory name for schema files"""

class Orchestra10:
    """
    Represents the XML schema for FIX Orchestra version 1.0 and processing of XML instances \
    that conform to that schema.
    """
    V1_0_DIR = 'v1-0'
    """Directory name for version 1.0 schema files"""

    FIXR_NAMESPACE = 'http://fixprotocol.io/2020/orchestra/repository'
    """Namespace for FIX Orchestra elements"""

    def __init__(self):
        self.xsd = XMLSchema(Orchestra10.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), SCHEMAS_DIR, cls.V1_0_DIR, )
        return os.path.join(schemas_dir, 'repository.xsd')

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
        for result in self.xsd.iter_decode(xml, use_defaults=False, validation='lax', converter=JsonMLConverter):
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
                                       namespaces={'fixr': self.FIXR_NAMESPACE,
                                                   'dcterms': 'http://purl.org/dc/terms/',
                                                   'dc': 'http://purl.org/dc/elements/1.1/'},
                                       **{'converter': JsonMLConverter})
        ElementTree.register_namespace(
            'fixr', self.FIXR_NAMESPACE)
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        stream.write(ElementTree.tostring(data, encoding='utf-8', method='xml'))
        return errors


class FixmlAppinfo:
    """
    Represents the XML schema for appinfo elements imported into Orchestra
    """
    APPINFO_DIR = 'appinfo'
    """Directory name for appinfo schema files"""

    def __init__(self):
        self.xsd = XMLSchema(FixmlAppinfo.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), SCHEMAS_DIR, cls.APPINFO_DIR)
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


Orchestra = Orchestra10WithAppinfo
""" Default Orchestra schema implementation """


class Orchestra11(Orchestra10):
    """
    Represents the XML schema for FIX Orchestra version 1.1 and processing of XML instances \
    that conform to that schema.
    """
    V1_1_DIR = 'v1-1'
    """Directory name for version 1.1 schema files"""

    FIXR_NAMESPACE = 'http://fixprotocol.io/2023/orchestra/repository'
    """Namespace for FIX Orchestra elements"""

    def __init__(self):
        self.xsd = XMLSchema(Orchestra11.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), SCHEMAS_DIR, cls.V1_1_DIR)
        return os.path.join(schemas_dir, 'repository.xsd')

    def read_xml(self, xml) -> Tuple[OrchestraInstance11, List[Exception]]:
        """
        Creates an OrchestraInstance11 and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        data, errors = [], []
        for result in self.xsd.iter_decode(xml, use_defaults=False, validation='lax', converter=JsonMLConverter):
            if not isinstance(result, Exception):
                data.append(result)
            else:
                errors.append(result)
        return OrchestraInstance11(data[0]), errors

    def write_xml(self, instance: OrchestraInstance11, stream) -> List[Exception]:
        """
        Encodes an OrchestraInstance11 and writes it to a stream.

        :param instance: an OrchestraInstance11 dictionary
        :param stream: a file like object
        :return: a list of errors, if any
        """
        data, errors = self.xsd.encode(instance.root(), validation='lax', use_defaults=False,
                                     namespaces={'fixr': self.FIXR_NAMESPACE,
                                               'dcterms': 'http://purl.org/dc/terms/',
                                               'dc': 'http://purl.org/dc/elements/1.1/'},
                                     **{'converter': JsonMLConverter})
        ElementTree.register_namespace('fixr', self.FIXR_NAMESPACE)
        ElementTree.register_namespace('dcterms', 'http://purl.org/dc/terms/')
        ElementTree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        stream.write(ElementTree.tostring(data, encoding='utf-8', method='xml'))
        return errors

