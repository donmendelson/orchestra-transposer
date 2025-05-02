from pprint import pformat
from typing import List, Optional, Tuple, Union


class OrchestraInstance10:
    """
    An instance of Orchestra version 1.0.
    Supports Dublin Core Terms metadata and appinfo elements for certain tools.
    """

    def __init__(self, obj=None):
        self.obj = obj if obj is not None else ['fixr:repository', {}]

    def __str__(self):
        return pformat(self.obj, width=120)

    def root(self) -> list:
        """
        :return: the root of an Orchestra instance represented as a Python dictionary
        """
        return self.obj

    def repository(self) -> dict:
        """ Returns attributes of a repository """
        try:
            return next(i for i in self.obj if isinstance(i, dict))
        except StopIteration:
            d = {}
            self.obj.append(d)
            return d

    def metadata(self) -> list:
        """
        :return: the metadata section of an Orchestra instance containing Dublin Core Terms
        """
        try:
            metadata = next(l for l in self.root() if isinstance(l, list) and l[0] == 'fixr:metadata')
        except StopIteration:
            metadata = ['fixr:metadata']
            self.root().append(metadata)
        return metadata

    def metadata_term(self, term: str) -> Optional[str]:
        """
        :return: the value of a Dublin Core Term metadata
        """
        metadata = self.metadata()
        return next((l[1] for l in metadata if isinstance(l, list) and l[0] == term), None)

    def _types(self, category: str) -> list:
        try:
            types = next(i for i in self.root() if isinstance(i, list) and i[0] == category)
        except StopIteration:
            types = [category]
            self.root().append(types)
        return types

    def sections(self) -> list:
        """
        :return: a list of sections of an Orchestra instance
        """
        return self._types('fixr:sections')

    def categories(self) -> list:
        """
        :return: a list of categories of an Orchestra instance
        """
        return self._types('fixr:categories')

    def category(self, name: str) -> Optional[list]:
        """
        :return: a category by name
        """
        categories = self.categories()
        return next((category for category in categories if isinstance(category, list) and category[1]['name'] == name),
                    None)

    def datatypes(self) -> list:
        """
        :return: a list of  datatypes of an Orchestra instance
        """
        return self._types('fixr:datatypes')

    def codesets(self) -> list:
        """
        :return: a list of  codesets of an Orchestra instance
        """
        return self._types('fixr:codeSets')

    def fields(self) -> list:
        """
        :return: a list of  fields of an Orchestra instance
        """
        return self._types('fixr:fields')

    def components(self) -> list:
        """
        :return: a list of  components of an Orchestra instance
        """
        return self._types('fixr:components')

    def groups(self) -> list:
        """
        :return: a list of  components of an Orchestra instance
        """
        return self._types('fixr:groups')

    def messages(self) -> list:
        """
        :return: a list of messages of an Orchestra instance
        """
        return self._types('fixr:messages')

    def append_message(self, message: list):
        """
        Add a message to this Orchestra instance

        :param message: a message is represented as a dictionary in the following format.

        .. code-block:: python

        ['fixr:message',
           {'abbrName': 'Heartbeat', 'added': 'FIX.2.7', 'category': 'Session', 'id': 1, 'msgType': '0', 'name': 'Heartbeat'},
           ['fixr:structure',
            ['fixr:componentRef',
             {'added': 'FIX.2.7', 'id': 1024, 'presence': 'required'},
             ['fixr:annotation', ['fixr:documentation', 'MsgType = 0']]],
            ['fixr:fieldRef',
             {'added': 'FIX.4.0', 'id': 112},
             ['fixr:annotation',
              ['fixr:documentation', 'Required when the heartbeat is the result of a Test Request message.']]],
            ['fixr:componentRef',
             {'added': 'FIX.2.7', 'id': 1025, 'presence': 'required'},
             ['fixr:annotation', ['fixr:documentation']]]],
           ['fixr:annotation',
            ['fixr:documentation',
             {'purpose': 'SYNOPSIS'},
             'The Heartbeat monitors the status of the communication link and identifies when the last of a string of messages '
             'was not received.']]],
        """
        messages = self.messages()
        messages.append(message)

    def append_component(self, component: list):
        components = self.components()
        components.append(component)

    def append_group(self, group: list):
        """
        Add a repeating group to this Orchestra instance

        :param group: a group is represented as a dictionary

        .. code-block:: python
          ['fixr:group',
           {'abbrName': 'Stip', 'added': 'FIX.4.4', 'category': 'Common', 'id': 1007, 'name': 'LegStipulations'},
           ['fixr:numInGroup', {'id': 683}, ['fixr:annotation', ['fixr:documentation']]],
           ['fixr:fieldRef',
            {'added': 'FIX.4.4', 'id': 688},
            ['fixr:annotation', ['fixr:documentation', 'Required if NoLegStipulations >0']]],
           ['fixr:fieldRef', {'added': 'FIX.4.4', 'id': 689}, ['fixr:annotation', ['fixr:documentation']]],
           ['fixr:annotation',
            ['fixr:documentation',
             {'purpose': 'SYNOPSIS'},
             'The LegStipulations component block has the same usage as the Stipulations component block, but for a leg '
             'instrument in a multi-legged security.'],
        """
        groups = self.groups()
        groups.append(group)

    @staticmethod
    def structure(message: list) -> list:
        try:
            return next(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:structure', message))
        except StopIteration:
            struct = ['fixr:structure']
            message.append(struct)
        return struct

    @staticmethod
    def documentation(element: list) -> List[Tuple[str, str]]:
        """ Returns a list of documentation elements, each a tuple of purpose (possibly None) and text """
        try:
            annotation = next(i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation')
            documentation = filter(lambda l: isinstance(l, list) and l[0] == 'fixr:documentation' and len(l) > 1,
                                   annotation)
            return list(map(OrchestraInstance10.__map_documentation, documentation))
        except StopIteration:
            return []

    @staticmethod
    def __map_documentation(element: list) -> Optional[Tuple[str, str]]:
        try:
            attr = next(i for i in element if isinstance(i, dict))
            purpose = attr['purpose']
        except StopIteration:
            purpose = None
        text = element[-1] if len(element) > 1 and isinstance(element[-1], str) else None
        return purpose, text

    @staticmethod
    def append_documentation(element: list, documentation: str):
        """ Appends an annotation with a single documentation string without Purpose """
        if str:
            annotation = next((i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation'), None)
            if not annotation:
                annotation = ['fixr:annotation']
                element.append(annotation)
            annotation.append(['fixr:documentation', {}, documentation])

    @staticmethod
    def append_documentations(element: list, documentations: List[Tuple[Union[str, dict, type(None)], List[str]]]):
        """
        Appends an annotation with one or more two-element tuples.

        The first element is one of the following:
        * A string for the value of purpose attribute
        * A dictionary. The acceptable keys are purpose, lang, and contentType.
        * None
        The second element is a list of text.
        """
        if len(documentations) > 0:
            annotation = next((i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation'), None)
            if not annotation:
                annotation = ['fixr:annotation']
                element.append(annotation)
            for documentation in documentations:
                attr = {}
                if documentation[0]:
                    if isinstance(documentation[0], dict):
                        attr = documentation[0]
                    elif isinstance(documentation[0], str):
                        attr = {'purpose': documentation[0]}
                if len(documentation[1]) == 0:
                    # add at least one documentation because annotation cannot be empty
                    annotation.append(['fixr:documentation', attr, ""])
                for text in documentation[1]:
                    annotation.append(['fixr:documentation', attr, text])

    @staticmethod
    def append_appinfo(element: list, appinfos: List[Tuple[dict, str]]):
        """
        Appends an annotation with one or more appinfo, each with a dictionary and text

        Standard dictionary keys are 'lang', 'purpose'.
        """
        if len(appinfos) > 0:
            annotation = next((i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation'), None)
            if not annotation:
                annotation = ['fixr:annotation']
                element.append(annotation)
            for appinfo in appinfos:
                l = ['fixr:appinfo']
                if appinfo[0]:
                    l.append(appinfo[0])
                if appinfo[1]:
                    l.append(appinfo[1])
                annotation.append(l)

    @staticmethod
    def append_fixml_appinfo(element: list, attributes: dict):
        """ Append appinfo for FIXML generator """
        if len(attributes) > 0:
            annotation = next((i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation'), None)
            if not annotation:
                annotation = ['fixr:annotation']
                element.append(annotation)
            l = ['fixr:appinfo', {'purpose': 'FIXML'}, ['fixml:FIXMLencodingType', attributes]]
            annotation.append(l)

    @staticmethod
    def appinfo(element: list, purpose: str) -> List[str]:
        """
        Returns a list of appinfo text for a given purpose

        :param element: the element with which the appinfo is associated
        :param purpose: typically an application name
        :return: a list of text, may be empty
        """
        try:
            annotation = next(i for i in element if isinstance(i, list) and i[0] == 'fixr:annotation')
            lst = filter(
                lambda l: isinstance(l, list) and l[0] == 'fixr:appinfo' and l[1].get('purpose', None) == purpose,
                annotation)
            return [a[2] for a in lst]
        except StopIteration:
            return []

    @staticmethod
    def field_refs(structure: list) -> list:
        """
        Returns a list of fieldRefs in a structure
        :param structure: a message, component, or group
        :return: a list of fieldRefs, which may be empty
        """
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:fieldRef', structure))

    @staticmethod
    def component_refs(structure: list) -> list:
        """
        Returns a list of componentRefs in a structure
        :param structure: a message, component, or group
        :return: a list of componentRefs, which may be empty
        """
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:componentRef', structure))

    @staticmethod
    def group_refs(structure: list) -> list:
        """
        Returns a list of groupsRefs in a structure
        :param structure: a message, component, or group
        :return: a list of groupRefs, which may be empty
        """
        return list(filter(lambda l: isinstance(l, list) and l[0] == 'fixr:groupRef', structure))

    def field(self, field_id: int) -> Optional[list]:
        fields: list = self.fields()
        return next((field for field in fields if isinstance(field, list) and field[1]['id'] == field_id), None)

    def field_by_name(self, field_name: str) -> Optional[list]:
        fields: list = self.fields()
        return next((field for field in fields if isinstance(field, list) and field[1]['name'].casefold() ==
                     field_name.casefold()), None)

    def field_data_field(self, length_id: int) -> Optional[list]:
        """
        Finds a data field associated to a Length field
        :param length_id: tag of a length field
        :return: a data field if found, or None
        """
        fields: list = self.fields()
        return next((field for field in fields if isinstance(field, list) and field[1].get('lengthId', None) ==
                     length_id), None)

    def component(self, component_id: int) -> Optional[list]:
        components: list = self.components()
        return next((component for component in components if
                     isinstance(component, list) and component[1]['id'] == component_id), None)

    def component_by_name(self, component_name: str) -> Optional[list]:
        components: list = self.components()
        return next((component for component in components if
                     isinstance(component, list) and component[1]['name'].casefold() == component_name.casefold()),
                    None)

    def group(self, group_id: int) -> Optional[list]:
        groups: list = self.groups()
        return next((group for group in groups if isinstance(group, list) and group[1]['id'] == group_id), None)

    def group_by_name(self, group_name: str) -> Optional[list]:
        groups: list = self.groups()
        return next((group for group in groups if
                     isinstance(group, list) and group[1]['name'].casefold() == group_name.casefold()), None)

    def codeset_by_name(self, codeset_name: str) -> Optional[list]:
        codesets: list = self.codesets()
        return next(
            (codeset for codeset in codesets if
             isinstance(codeset, list) and codeset[1]['name'].casefold() == codeset_name.casefold()), None)

    @staticmethod
    def append_field_ref(structure: list, field_ref):
        """
        Append a fieldRef to a message or group structure
        """
        try:
            pos = next(i for i in reversed(range(len(structure))) if isinstance(structure[i], list) and
                       structure[i][0] == 'fixr:annotation')
            structure.insert(pos, field_ref)
        except StopIteration:
            structure.append(field_ref)

    @staticmethod
    def append_group_ref(structure: list, group_ref):
        """
        Append a groupRef to a message or group structure
        """
        try:
            pos = next(i for i in reversed(range(len(structure))) if isinstance(structure[i], list) and
                       structure[i][0] == 'fixr:annotation')
            structure.insert(pos, group_ref)
        except StopIteration:
            structure.append(group_ref)


class OrchestraInstance11(OrchestraInstance10):
    """
    An instance of Orchestra version 1.1.
    Extends Orchestra 1.0 with additional features and improvements.
    """
    
    def __init__(self, obj=None):
        super().__init__(obj)
        # Add any version 1.1 specific initialization here

    def __str__(self):
        return f"Orchestra 1.1 Instance:\n{super().__str__()}"

    def scenarios(self) -> list:
        """
        :return: a list of scenarios of an Orchestra instance
        """
        return self._types('fixr:scenarios')

    def scenario(self, scenario_id: int) -> Optional[list]:
        """
        Finds a scenario by its numeric ID
        :param scenario_id: numeric ID of the scenario
        :return: a scenario if found, or None
        """
        scenarios: list = self.scenarios()
        return next((scenario for scenario in scenarios if 
                    isinstance(scenario, list) and scenario[1]['id'] == scenario_id), None)

    def scenario_by_name(self, scenario_name: str) -> Optional[list]:
        """
        Finds a scenario by its name
        :param scenario_name: name of the scenario
        :return: a scenario if found, or None
        """
        scenarios: list = self.scenarios()
        return next((scenario for scenario in scenarios if 
                    isinstance(scenario, list) and scenario[1]['name'].casefold() == scenario_name.casefold()), None)

    def append_scenario(self, scenario: list):
        """
        Add a scenario to this Orchestra instance

        :param scenario: a scenario is represented as a list in the following format.

        .. code-block:: python
          ['fixr:scenario',
           {'id': 1, 'name': 'ExampleScenario'},
           ['fixr:annotation',
            ['fixr:documentation',
             {'purpose': 'SYNOPSIS'},
             'Description of the scenario']]]
        """
        scenarios = self.scenarios()
        scenarios.append(scenario)

    # Add any version 1.1 specific methods here
    # For example, if there are new features in 1.1 that aren't in 1.0

OrchestraInstance = OrchestraInstance10
"""Default Orchestra instance"""
