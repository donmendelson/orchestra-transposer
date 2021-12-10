import os
from typing import List, Tuple
from xml.etree import ElementTree

from xmlschema import JsonMLConverter, XMLSchema

from .unifiedinstance import UnifiedMainInstance, UnifiedInstanceWithPhrases, \
    UnifiedPhrasesInstance


class UnifiedMain:
    """
    Represents the XML schema for FIX Unified Repository 2010 Edition and processing of XML instances \
    that conform to that schema.
    """

    def __init__(self):
        schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas/')
        repository_xsd_path = os.path.join(schemas_dir, 'FixRepository.xsd')
        self.xsd = XMLSchema(repository_xsd_path)

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

    def read_xml(self, xml) -> Tuple[UnifiedMainInstance, List[Exception]]:
        """
        Creates an UnifiedInstance and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        data, errors = [], []
        for result in self.xsd.iter_decode(xml, use_defaults=False, converter=JsonMLConverter):
            if not isinstance(result, Exception):
                data.append(result)
            else:
                errors.append(result)
        return UnifiedMainInstance(data[0]), errors

    def write_xml(self, instance: UnifiedMainInstance, stream) -> List[Exception]:
        """
        Encodes an UnifiedInstance and writes it to a stream.

        :param instance: an UnifiedInstance dictionary
        :param stream: a file like object
        :return: a list of errors, if any
        """
        data, errors = self.xsd.encode(
            instance.root(), validation='lax', use_defaults=False, path="fixRepository",
            **{'converter': JsonMLConverter})
        stream.write(ElementTree.tostring(data, encoding='utf8', method='xml'))
        return errors


class UnifiedPhrases:
    """
    Represents the XML schema for FIX Unified Repository 2010 Edition and processing of XML instances \
    that conform to that schema.
    """

    def __init__(self):
        schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas/')
        phrases_xsd_path = os.path.join(schemas_dir, 'FixPhrases.xsd')
        self.xsd = XMLSchema(phrases_xsd_path)

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

    def read_xml(self, xml) -> Tuple[UnifiedPhrasesInstance, List[Exception]]:
        """
        Creates an UnifiedInstance and a possible List of validation errors.

        :param xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        """
        data, errors = [], []
        for result in self.xsd.iter_decode(xml, use_defaults=False, converter=JsonMLConverter):
            if not isinstance(result, Exception):
                data.append(result)
            else:
                errors.append(result)
        return UnifiedPhrasesInstance(data[0]), errors

    def write_xml(self, instance: UnifiedPhrasesInstance, stream) -> List[Exception]:
        """
        Encodes an UnifiedInstance and writes it to a stream.

        :param instance: an UnifiedInstance dictionary
        :param stream: a file like object
        :return: a list of errors, if any
        """
        data, errors = self.xsd.encode(
            instance.phrases_root(), validation='lax', use_defaults=False,
            **{'converter': JsonMLConverter})
        stream.write(ElementTree.tostring(data, encoding='utf8', method='xml'))
        return errors


class UnifiedWithPhrases:
    """
    Represents the XML schema for FIX Unified Repository 2010 Edition and processing of XML instances \
    that conform to that schema.
    """

    def __init__(self):
        self.unified = UnifiedMain()
        self.phrases = UnifiedPhrases()

    def validate_all(self, unified_xml, phrases_xml) -> Tuple[List[Exception], List[Exception]]:
        """
        Validates an XML data against the XSD schema/component instance. Creates an iterator for the errors generated
        by the validation of an XML data against the XSD schema/component instance.

        :param unified_xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        :param phrases_xml: the source of XML data for phrases
        :return a pair of lists of exceptions, one for the main XML file, and the second for the phrases file
        """
        errors = self.unified.validate(unified_xml)
        return errors, self.phrases.validate(phrases_xml)

    def read_xml_all(self, unified_xml, phrases_xml) -> Tuple[UnifiedInstanceWithPhrases, List[Exception]]:
        """
        Creates an UnifiedInstance and a possible List of validation errors.

        :param unified_xml: the source of XML data. Can be an :class:`XMLResource` instance, a \
        path to a file or an URI of a resource or an opened file-like object or an Element \
        instance or an ElementTree instance or a string containing the XML data.
        :param phrases_xml: the source of XML data for phrases
        """
        errors = []
        obj, unified_errors = self.unified.read_xml(unified_xml)
        errors.extend(unified_errors)
        phrases_obj, phrases_errors = self.phrases.read_xml(phrases_xml)
        errors.extend(phrases_errors)
        return UnifiedInstanceWithPhrases(obj, phrases_obj), errors

    def write_xml_all(self, instance: UnifiedInstanceWithPhrases, unified_stream, phrases_stream) -> List[Exception]:
        """
        Encodes an UnifiedInstance and writes it to a stream.

        :param instance: an UnifiedInstance dictionary
        :param unified_stream: a file like object for writing the main repository file
        :param phrases_stream: a file like object for writing the phrases file
        :return: a list of errors, if any
        """
        errors = self.unified.write_xml(instance.unified, unified_stream)
        errors.extend(self.phrases.write_xml(instance.phrases, phrases_stream))
        return errors


Unified = UnifiedWithPhrases
""" Default Unified Repository """
