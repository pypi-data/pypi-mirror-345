from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Dict, Optional
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json
@dataclass
class PropertyDefinition:
    """
    Definition of a property.

    Attributes:
    - name (str): Name of the property.
    - kind (str): Kind of the property (e.g. 'CI', 'string').
    - category (str): Category of the property (e.g. 'input', 'output').
    - password (bool): Whether the property is a password.
    - value (Any): Value of the property.
    """
    name: str
    kind: str
    category: str
    password: bool
    value: Any

    def property_value(self):
        """
        Get the value of the property, recursively unwrapping nested CI properties.

        Returns:
        - Any: The value of the property.
        """
        if self.kind == 'CI' and self.value:
            ci = CiDefinition.from_dict(self.value)
            return {p.name: p.property_value() for p in ci.properties}
        else:
            return self.value

    def secret_value(self):
        """
        Get the password values of the property, recursively unwrapping nested CI properties.

        Returns:
        - list: A list of password values.
        """
        if self.kind == 'CI' and self.value:
            ci = CiDefinition.from_dict(self.value)
            return [p.value for p in ci.properties if p.password and p.value]
        else:
            return [self.value] if self.password and self.value else []


@dataclass_json
@dataclass
class CiDefinition:
    """
    Definition of a CI.

    Attributes:
    - id (str): ID of the CI.
    - type (str): Type of the CI.
    - properties (List[PropertyDefinition]): List of properties for the CI.
    """
    id: str
    type: str
    properties: List[PropertyDefinition]


@dataclass_json
@dataclass
class TaskContext(CiDefinition):
    """
    Context of a task.

    Attributes:
    - id (str): ID of the CI.
    - type (str): Type of the CI.
    - properties (List[PropertyDefinition]): List of properties for the CI.
    """

    def output_properties(self) -> List[str]:
        """
        Get the names of the output properties of the task.

        Returns:
        - list: A list of output property names.
        """
        return [p.name for p in self.properties if p.category == 'output']

    def secrets(self) -> List[str]:
        """
        Get the password values of the task, recursively unwrapping nested CI properties.

        Returns:
        - list: A list of password values.
        """
        secret_list = []
        for p in self.properties:
            secret_list.extend(p.secret_value())
        return secret_list

    def build_locals(self) -> Dict[str, Any]:
        """
        Build a dictionary of the task's property values.

        Returns:
        - dict: A dictionary of property names to values.
        """
        return {p.name: p.property_value() for p in self.properties}

    def script_location(self) -> str:
        """
        Get the value of the 'scriptLocation' property.

        Returns:
        - str: The value of the 'scriptLocation' property.
        """
        return next(p.value for p in self.properties if p.name == 'scriptLocation')


@dataclass_json
@dataclass
class AutomatedTaskAsUserContext:
    """
    Context for running an automated task as a specific user.

    Attributes:
    - username (str): The username to run the task as.
    - password (str): The password for the user.
    """
    username: Optional[str]
    password: Optional[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ReleaseContext:
    """
    Context of a release.

    Attributes:
    - id (str): ID of the release.
    - automated_task_as_user (AutomatedTaskAsUserContext): Context for running
        an automated task as a specific user.
    """
    id: str
    automated_task_as_user: AutomatedTaskAsUserContext


@dataclass_json()
@dataclass
class InputContext:
    """
    Input context for a task.

    Attributes:
    - release (ReleaseContext): Context of the release.
    - task (TaskContext): Context of the task.
    """
    release: ReleaseContext
    task: TaskContext

