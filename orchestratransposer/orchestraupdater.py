import logging
from typing import List, Set, Tuple

from orchestra.orchestra import Orchestra10, Orchestra11
from orchestra.orchestrainstance import OrchestraInstance10, OrchestraInstance11


class Orchestra10_11Updater:
    def __init__(self):
        self.logger = logging.getLogger('orchestraupdater')

    def update_dict(self, orch10: OrchestraInstance10) -> OrchestraInstance11:
        """
        Update an Orchestra 1.0 dictionary to an Orchestra 1.1 dictionary
        :param orch10: an Orchestra version 1.0 data dictionary
        :return: an Orchestra version 1.1 data dictionary
        """
        orch11 = OrchestraInstance11()
        self.update_metadata(orch10, orch11)
        self.update_datatypes(orch10, orch11)
        self.update_codesets(orch10, orch11)
        self.update_fields(orch10, orch11)
        self.update_components(orch10, orch11)
        self.update_groups(orch10, orch11)
        self.update_messages(orch10, orch11)
        self.update_scenarios(orch10, orch11)
        return orch11

    def update_xml(self, orchestra10_xml, orchestra11_stream) -> List[Exception]:
        """
        Update an Orchestra 1.0 file to an Orchestra 1.1 file
        :param orchestra10_xml: an XML file-like object in Orchestra 1.0 schema
        :param orchestra11_stream: an output stream to write an Orchestra 1.1 file
        :return: a list of errors, if any
        """
        orchestra10 = Orchestra10()
        (orch10_instance, errors) = orchestra10.read_xml(orchestra10_xml)
        if errors:
            for error in errors:
                self.logger.error(error)
            return errors
        else:
            orch11_instance = self.update_dict(orch10_instance)
            orchestra11 = Orchestra11()
            errors = orchestra11.write_xml(orch11_instance, orchestra11_stream)
            for error in errors:
                self.logger.error(error)
            return errors

    def update_metadata(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update metadata from Orchestra 1.0 to 1.1
        """
        repository = orch10.repository()
        repository['xmlns:fixr'] = Orchestra11.FIXR_NAMESPACE
        repository.pop('xsi:schemaLocation', None)
        orch11.repository().update(repository)
        metadata = orch10.metadata()
        for item in metadata:
            if isinstance(item, list):
                orch11.metadata().append(item)

    def update_datatypes(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update datatypes from Orchestra 1.0 to 1.1
        """
        datatypes = orch10.datatypes()
        for datatype in datatypes:
            if isinstance(datatype, list):
                orch11.datatypes().append(datatype)

    def update_codesets(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update codesets from Orchestra 1.0 to 1.1
        """
        codesets = orch10.codesets()
        for codeset in codesets:
            if isinstance(codeset, list):
                # Update each code in the codeset
                codes = [c for c in codeset if isinstance(c, list) and len(c) > 1 and c[0] == 'fixr:code']
                for code in codes:
                    self.update_code(code)
                # Update the codeset itself
                orch11.codesets().append(codeset)

    def update_code(self, code):
        """
        Update a single code from Orchestra 1.0 to 1.1 format
        :param code: A code dictionary to update
        """
        if 'sort' in code[1]:
            try:
                code[1]['sort'] = int(code[1]['sort'])
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert sort value '{code[1]['sort']}' to integer")

    def update_fields(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update fields from Orchestra 1.0 to 1.1
        """
        fields = orch10.fields()
        for field in fields:
            if isinstance(field, list):
                orch11.fields().append(field)

    def update_components(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update components from Orchestra 1.0 to 1.1
        """
        components = orch10.components()
        for component in components:
            if isinstance(component, list):
                orch11.components().append(component)

    def update_groups(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update groups from Orchestra 1.0 to 1.1
        """
        groups = orch10.groups()
        for group in groups:
            if isinstance(group, list):
                orch11.groups().append(group)

    def update_messages(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update messages from Orchestra 1.0 to 1.1
        """
        messages = orch10.messages()
        for message in messages:
            if isinstance(message, list):
                orch11.messages().append(message)

    def update_scenarios(self, orch10: OrchestraInstance10, orch11: OrchestraInstance11):
        """
        Update scenarios from Orchestra 1.0 to 1.1 by collecting unique scenario identifiers
        from various elements and creating a formal scenarios section.
        """
        # Collect unique scenario names and their associated IDs
        scenario_info: Set[Tuple[str, int]] = set()
        
        # Check fields for scenarios
        for field in orch10.fields():
            if isinstance(field, list) and len(field) > 1 and isinstance(field[1], dict):
                scenario = field[1].get('scenario', 'base')
                scenario_id = field[1].get('scenarioId', 1)
                scenario_info.add((scenario, scenario_id))
        
        # Check groups for scenarios
        for group in orch10.groups():
            if isinstance(group, list) and len(group) > 1 and isinstance(group[1], dict):
                scenario = group[1].get('scenario', 'base')
                scenario_id = group[1].get('scenarioId', 1)
                scenario_info.add((scenario, scenario_id))
        
        # Check messages for scenarios
        for message in orch10.messages():
            if isinstance(message, list) and len(message) > 1 and isinstance(message[1], dict):
                scenario = message[1].get('scenario', 'base')
                scenario_id = message[1].get('scenarioId', 1)
                scenario_info.add((scenario, scenario_id))
        
        # Create scenarios section
        for scenario_name, scenario_id in scenario_info:
            scenario = ['fixr:scenario', {'id': scenario_id, 'name': scenario_name}]
            orch11.append_scenario(scenario)


OrchestraUpdater = Orchestra10_11Updater
"""Updates Orchestra version 1.0 to Orchestra version 1.1""" 