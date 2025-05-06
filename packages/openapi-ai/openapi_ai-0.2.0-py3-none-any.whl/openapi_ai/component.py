from typing import Dict, Any
from .schema import process_schema

def generate_components(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a dictionary of components from an OpenAPI specification.

    The dictionary returned by this function has the same structure as the 'components'
    section of an OpenAPI specification. Each key in the dictionary corresponds to the
    name of a component, and the value associated with that key is a list of fields
    that make up the component.

    Each field is a dictionary with the following keys:
    - 'name': The name of the field.
    - 'type': The type of the field.
    - 'description': A description of the field.
    - 'required': A boolean indicating whether the field is required.

    :param spec: An OpenAPI specification.
    :return: A dictionary of components.
    """
    components = {}

    for key in spec['components']['schemas'].keys():
        component = spec['components']['schemas'][key]
        properties = component['properties']
        required = component['required'] if 'required' in component else []

        fields = []

        for prop_key, prop_value in properties.items():

            prop_description = prop_value['description'] if 'description' in prop_value else ""

            _type = process_schema(prop_value)

            field = {
                "name": prop_key,
                "type": _type,
                "description": prop_description,
                "required": prop_key in required,
            }
            fields.append(field)

        components[key] = fields

    return components
