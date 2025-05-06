from .type import convert_type_to_python

def process_schema(schema: dict, components: dict | None = None):
    """
    Processes an OpenAPI schema definition and returns a corresponding Python type annotation.

    This function handles schema references, primitive types, and complex compositions
    like 'anyOf', 'oneOf', and 'allOf'. It can also resolve references to other components
    if provided.

    Args:
        schema (dict): The OpenAPI schema definition to process.
        components (dict | None): Optional dictionary of components to resolve references.

    Returns:
        str: A string representing the Python type annotation.
    """

    ref = schema.get('$ref')
    type_ = None

    if ref:
        ref_name = ref.removeprefix("#/components/schemas/")
        return components[ref_name]

    type_ = convert_type_to_python(schema.get('type'))

    if 'anyOf' in schema:
        any_of = schema['anyOf']
        types = []
        for any_of_item in any_of:
            types.append(process_schema(any_of_item))
        type_ = " | ".join(types)
    elif 'oneOf' in schema:
        one_of = schema['oneOf']
        types = []
        for one_of_item in one_of:
            types.append(process_schema(one_of_item))
        type_ = " | ".join(types)
    elif 'allOf' in schema:
        all_of = schema['allOf']
        types = []
        for all_of_item in all_of:
            types.append(process_schema(all_of_item))
        type_ = " & ".join(types)

    return type_
