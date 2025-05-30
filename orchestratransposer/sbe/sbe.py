import os
import xml.etree.ElementTree as ET
from typing import List, Tuple

import xmlschema
from xmlschema import JsonMLConverter

from .sbeinstance import SBEInstance10, SBEInstance20


class SBE10:
    """
    Represents the XML schema for Simple Binary Encoding version 1.0 and processing of XML instances \
    that conform to that schema.
    """

    SBE_PRIMITIVE_TYPES = ['char', 'int8', 'int16', 'int32', 'int64',
                           'uint8', 'uint16', 'uint32', 'uint64', 'float', 'double']

    def __init__(self):
        self.xsd = xmlschema.XMLSchema(SBE10.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas/')
        return os.path.join(schemas_dir, 'sbe.xsd')

    def validate(self, xml) -> List[Exception]:
        """
        Validates an XML data against the XSD schema/component instance. Creates an iterator for the errors generated by
        the validation of an XML data against the XSD schema/component instance.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        errors = []
        for result in self.xsd.iter_errors(xml):
            errors.append(result)
        return errors

    def read_xml(self, xml) -> Tuple[SBEInstance10, List[Exception]]:
        """
        Creates an SBEInstance and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        :return: a list of errors, if any
        """
        data, errors = [], []
        # JsonMLConverter preserves order
        for result in self.xsd.iter_decode(xml, validation='lax', use_defaults=False, converter=JsonMLConverter):
            if not isinstance(result, Exception):
                data.append(result)
            else:
                errors.append(result)
        return SBEInstance10(data[0] if len(data) > 0 else None), errors

    def write_xml(self, sbe_instance: SBEInstance10, stream) -> List[Exception]:
        """
        Encodes an SBEInstance and writes it to a stream, returns a possible List of validation errors.

        :param sbe_instance: an SBE instance
        :param stream: a file like object

        :return: a list of errors, if any
        """
        data, errors = self.xsd.encode(sbe_instance.root(), validation='lax', use_defaults=False,
                                       namespaces={'sbe': 'http://fixprotocol.io/2016/sbe'},
                                       **{'converter': JsonMLConverter})
        ET.register_namespace('sbe', "http://fixprotocol.io/2016/sbe")
        stream.write(ET.tostring(data, encoding='utf-8', method='xml'))
        return errors


SBE = SBE10
""" Default SBE schema implementation """


class SBE20:
    """
    Represents the XML schema for Simple Binary Encoding version 2.0 release candidate and processing of XML instances \
    that conform to that schema.
    """

    def __init__(self):
        self.xsd = xmlschema.XMLSchema(SBE20.get_xsd_path())

    @classmethod
    def get_xsd_path(cls):
        schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas/')
        return os.path.join(schemas_dir, 'sbe-2.0rc3.xsd')

    def validate(self, xml) -> List[Exception]:
        """
        Validates an XML data against the XSD schema/component instance. Creates an iterator for the errors generated by
        the validation of an XML data against the XSD schema/component instance.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        errors = []
        for result in self.xsd.iter_errors(xml):
            errors.append(result)
        return errors

    def read_xml(self, xml) -> Tuple[SBEInstance20, List[Exception]]:
        """
        Creates an SBEInstance and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        :return: a list of errors, if any
        """
        data, errors = [], []
        # JsonMLConverter preserves order
        for result in self.xsd.iter_decode(xml, validation='lax', use_defaults=False, converter=JsonMLConverter):
            if not isinstance(result, Exception):
                data.append(result)
            else:
                errors.append(result)
        return SBEInstance20(data[0] if len(data) > 0 else None), errors

    def write_xml(self, sbe_instance: SBEInstance10, stream) -> List[Exception]:
        """
        Encodes an SBEInstance and writes it to a stream, returns a possible List of validation errors.

        :param sbe_instance: an SBE instance
        :param stream: a file like object

        :return: a list of errors, if any
        """
        data, errors = self.xsd.encode(sbe_instance.root(), validation='lax', use_defaults=False,
                                       namespaces={'': 'http://fixprotocol.io/2017/sbe'},
                                       **{'converter': JsonMLConverter})
        # ET.register_namespace('sbe', "http://fixprotocol.io/2017/sbe")
        stream.write(ET.tostring(data, encoding='utf-8', method='xml'))
        return errors
