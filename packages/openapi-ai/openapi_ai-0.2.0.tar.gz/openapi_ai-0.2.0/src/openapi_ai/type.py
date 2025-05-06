def convert_type_to_python(type_: str) -> str:
    """
    Maps OpenAPI types to Python type annotations.

    Given an OpenAPI type, returns a string representing the corresponding Python type annotation.
    If the OpenAPI type is not found in the mapping, the function returns 'Any'.

    Args:
        type_ (str): The OpenAPI type to map.

    Returns:
        str: The corresponding Python type annotation.
    """
    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List[Any]",
        "object": "Dict[str, Any]",
        "null": "None",
    }
    return type_map.get(type_, "Any")
