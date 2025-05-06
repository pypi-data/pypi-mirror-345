from __future__ import annotations
from typing import get_args, get_type_hints, Any, get_origin
from types import FunctionType, NoneType, UnionType, MethodType
import json, inspect, copy

RED   = "\033[31m"
WHITE = "\033[37m"


class InvalidInput(Exception):
    def __init__(self, message: str = "Invalid Input") -> None:
        super().__init__(message)


class TypeMismatch(Exception):
    def __init__(self, message: str = "Type mismatch") -> None:
        super().__init__(message)


class MissingKey(Exception):
    def __init__(self, message: str = "Missing key") -> None:
        super().__init__(message)


class JSONSchemaType:
    def __init__(self, schema_type: dict, required: bool = False) -> None:
        self.schema_type: dict = schema_type
        self.required: bool = required


# Get an objects __init__ function
# Return None if it doesn't have one
def __get_init__(obj: type) -> FunctionType | None:
    if not hasattr(obj, "__init__"):
        return None
    attr = getattr(obj, "__init__", None)
    if type(attr) != FunctionType:
        return None
    return attr


# Converts a type to a direct JSON Schema type
# str -> "string"
# Returns none if it has no match
def to_direct_json_schema_type(t: type) -> str | None:
    """
    Convert a type into a basic JSON Schema type string
    Ex: str -> "string"

    :param t: The type

    Supports the following types:

        str -> "string"
        float -> "number"
        int -> "integer"
        bool -> "boolean"
        NoneType -> "null"
        list -> "array"

    Anything else returns None

    |
    """
    if t == str:
        return "string"
    if t == float:
        return "number"
    if t == int:
        return "integer"
    if t == bool:
        return "boolean"
    if t == NoneType:
        return "null"
    if t == list:
        return "array"
    return None


# Converts a type, tuple of types, or list of types into a JSON Schema type
# str -> {"type": "string"}
def to_json_schema_type(t: type | tuple[type] | list[type], pull_descriptions: bool = False) -> JSONSchemaType:
    """
    Convert a type into a JSON Schema Type object

    :param t: The type
    :param pull_descriptions: Optional. Whether or not to pull descriptions if the function ends up generating a JSON Schema from an object

    Examples:

        to_json_schema_type(str)
        # Returns
        JSONSchemaType(schema_type={"type": "string"}, required=True)

    Multiple types can be input as a list or tuple

        to_json_schema_type([str, int])
        # Returns
        JSONSchemaType(schema_type={"anyOf": [{"type": "string"}, {"type": "integer"}]}, required=True)

    |
    """
    # Converts a list of types into a JSON Schema type dict
    # [str, int] -> {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    def __many__(tl: list[type]) -> JSONSchemaType:
        required: bool = False
        if NoneType in tl:
            required = True
            tl.remove(NoneType)
            if len(tl) == 1:
                schema_type: JSONSchemaType = to_json_schema_type(tl[0], pull_descriptions)
                schema_type.required = False
                return schema_type
        return JSONSchemaType({
            "anyOf": [to_json_schema_type(ty, pull_descriptions) for ty in tl]
        }, required)
    # First, attempt to get a basic string type
    # str -> "string"
    str_type: str | None = to_direct_json_schema_type(t)
    if str_type:
        # If a match is found, return it as a JSON Schema type dict
        return JSONSchemaType({
            "type": str_type
        }, True)
    # If no match is found, break down the type further
    origin: type = get_origin(t)
    arguments: tuple = get_args(t)
    # Check if it is a specified list, ex: list[str]
    if origin == list:
        # If it is, convert its specified types to JSON Schema types and return the final JSON Schema type 
        return JSONSchemaType({
            "type": "array",
            "items": to_json_schema_type(arguments, pull_descriptions).schema_type
        }, True)
    # Otherwise, check if it's a Union, ex: str | int
    if origin == UnionType:
        # If it is, convert it to a anyOf JSON Schema type dict and return it
        return __many__([argument for argument in arguments])
    # Otherwise, attempt to read it as a tuple or list
    length: int | None = None
    # If it cannot use the len function, it will fail and move on
    try:
        length = len(t)
    except:...
    if length:
        # If it can, then it is a tuple or list
        # If the length is one, just use the first type
        if length == 1:
            return to_json_schema_type(t[0], pull_descriptions)
        # If the length is zero, return {}
        elif length == 0:
            return JSONSchemaType({})
        # If there are multiple, return the many
        else:
            return __many__(t)
    # Otherwise, it must be an object
    return JSONSchemaType(generate_json_schema(t, pull_descriptions), True)


# Mold a value into a type
def mold_value(value: Any, expected_type: type):
    """
    Mold a value into a type. In other words, ensure a value is of an expected type, converting dicts of an object to an object

    :param value: The value
    :param expected_type: The type
    
    |
    """
    # If the value's type matches the expected type, no molded is needed
    if type(value) == expected_type:
        return value
    # Start by checking the origin of the expected type
    origin: type = get_origin(expected_type)
    # If the expected type is a list, then each item within the value needs to be molded
    if origin == list:
        # Prepare a list of molded values
        molded_values: list = []
        # For each item in the value...
        for item in value:
            # Attempt to mold the value into each type the list allows
            molded: bool = False
            for t in get_args(expected_type):
                try:
                    molded_values.append(mold_value(item, t))
                    molded = True
                    break
                except:...
            # If the item wasn't able to be molded into any of the types in the list, raise an error
            if not molded:
                raise TypeMismatch(f"Value \033[31m{value}\033[37m could not be molded into any of the expected types \033[31m{arguments}\033[37m")
        # Return the molded list
        return molded_values
    # If the expected type is Union...
    if origin == UnionType:
        # Attempt to mold the value into each type the Union allows
        for t in get_args(expected_type):
            try:
                return mold_value(value, t)
            except:...
        # If the value wasn't able to be molded into any of the types the Union allows, raise an error
        raise TypeMismatch(f"Value \033[31m{value}\033[37m could not be molded into any of the expected types \033[31m{arguments}\033[37m")
    # If the value's type didn't match the expected type and the expected type isn't a list or a union, then attempt to convert to an object
    
    if type(value) == dict:
        # Try to get the objects type hints
        type_hints: dict = get_type_hints(expected_type)
        if type_hints == {}:
            # If the object didn't have any type hints, try to get it's __init__ function
            init: FunctionType | None = __get_init__(expected_type)
            if init:
                type_hints = get_type_hints(init)
        # If the type hints were retreived
        if type_hints:
            # Prepare the molded values
            molded_values: dict | None = {}
            # For each key and item in value, attempt to mold it into the expect type
            for key, item in value.items():
                # If the key isn't in the type hints, cancel the molding
                if key not in type_hints:
                    molded_values = None
                    break
                molded_values[key] = mold_value(item, type_hints[key])
            # If the value's items were molded successfully...
            if molded_values:
                # Initialize the object with the molded values
                return expected_type(**molded_values)
    # If everything failed, raise an error
    raise TypeMismatch(f"Value \033[31m{value}\033[37m could not be molded into \033[31m{expected_type}\033[37m")


# Creates a JSON Schema
def create_json_schema(properties: list[str],
                       type_hints: dict[str, type] | None = None,
                       defaults: dict[str, Any] | None = None,
                       descriptions: dict[str, str]| None = None,
                       required: list[str] | None = None,
                       title: str | None = None,
                       pull_descriptions: bool = False,
                       pull_required: bool = False) -> dict:
    """
    Creates a JSON Schema

    :param properties: The list of properties. Ex: ["mystring", "myinteger"]
    :param type_hints: Optional. Types for any variables. Ex: {"mystring": str}
    :param defaults: Optional. Defaults for any variables. Ex: {"mystring": "Hello world!"}
    :param descriptions: Optional. Descriptions for any variables. Ex: {"mystring": "A basic string property."}
    :param title: Optional. The title of the schema
    :param pull_descriptions: Optional. Whether or not to pull descriptions if the function ends up generating a JSON Schema from an object
    :param pull_required: Option. Whether or not to mark a property required if it isn't a Union with NoneType. Ex. str -> Not required, str | None -> Required
    :returns: The JSON Schema dict

    |
    """
    # Prepare the base dict
    schema: dict = {
        "type": "object"
    }
    # If required properties are given, apply them
    if required:
        schema["required"] = required
    # If a title is given, apply it
    if title:
        schema["title"] = title
    # Prepare the properties dict
    props: dict = {}
    # For each property given
    for p in properties:
        # If its type was given, apply it
        if type_hints and p in type_hints:
            # Converts the type to a valid JSON Schema type
            schema_type: JSONSchemaType = to_json_schema_type(type_hints[p], pull_descriptions)
            if schema_type.required and pull_required:
                if "required" in schema and p not in schema["required"]:
                    schema["required"].append(p)
                else:
                    schema["required"] = [p]
            props[p] = schema_type.schema_type
        else:
            # Otherwise, prepare the property with an empty dictionary
            props[p] = {}
        # If its default value was given, apply it
        if defaults and p in defaults:
            props[p]["default"] = defaults[p]
        # If its description was given, apply it
        if descriptions and p in descriptions:
            props[p]["description"] = descriptions[p]
    # Apply the built properties dict
    schema["properties"] = props
    return schema


# Add descriptions to a JSON Schema
def describe_json_schema(schema: dict, descriptions: dict[str, str | dict]) -> dict:
    """
    Add descriptions to a JSON Schema

    :param schema: The JSON Schema
    :param descriptions: The descriptions
    :returns: The described JSON Schema

    The descriptions should be a dictionary of the property names to descriptions.
    
        {
            "propertyname": "Description"
        }

    If you need to describe a child property, use a dictionary in the description.

        {
            "propertyname": {
                "subpropertyname": "Description"
            }
        }
    
    If you need to describe a child property while also describing the parent property, use a formated dictionary:

        {
            "parentname": {
                "properties": {
                    "childname": "Child's description"
                },
                "description": "Parent's description"
            }
        }

    |
    """
    # Make a copy of the schema
    described: dict = copy.deepcopy(schema)
    # If the given schema doesn't have properties, then there's nothing to do
    if "properties" in described:
        # For each description given
        for k, v in descriptions.items():
            # If it is just a string, set the property's description
            if type(v) == str:
                if k in described["properties"]:
                    described["properties"][k]["description"] = v
            # If it is a dict, then it is describing child properties
            elif type(v) == dict:
                # If the dict includes description and properties, then that means it is defining the property and it's child properties
                if "description" in v and "properties" in v:
                    described["properties"][k] = describe_json_schema(described["properties"][k], v["properties"])
                    described["properties"][k]["description"] = v["description"]
                # Otherwise, it is just describing its child properties
                else:
                    described["properties"][k] = describe_json_schema(described["properties"][k], v)
    return described


# Pulls parameter descriptions from docstring params
def pull_docstring_parameters(obj) -> dict:
    """
    Pull parameters from an object or function's docstring using the reStructuredText (reST) format
    """
    # Prepare the descriptions
    descriptions: dict[str] = {}
    # Get the objects docstring
    doc: str | None = inspect.getdoc(obj)
    # If the object doesn't have a docstring, then return an empty dictionary
    if doc == None:
        return {}
    # Go through the docstring line by line
    for line in doc.split("\n"):
        # If the line starts with ":param " then it is a parameter
        if line.startswith(":param "):
            # Split up the line to get the name and description
            data: list[str] = line.removeprefix(":param ").split(": ")
            # Ignore any parameters that don't have the expected format
            # :param variableName: The variable description
            if len(data) != 2:
                continue
            # If the parameter is valid, add it to the descriptions
            descriptions[data[0]] = data[1]
    return descriptions


# Convert a function or object into a basic JSON Schema
# Pulls descriptions from docstrings
# function(variable: str) -> {"title": "function", "type": "object", "properties": {"variable": {"type": "string"}}}
def generate_json_schema(obj: FunctionType | type, pull_descriptions: bool = True) -> dict | None:
    """
    Convert a function or object into a JSON
    
    It can pull descriptions from docstrings using the reStructuredText (reST) format

    :param obj: The function or object
    :returns: A JSON Schema dict or None

    Examples:
 
        def my_function(variable: str):
            pass

        generate_json_schema(my_function)
        # Converts to:
        {
            "title": "my_function",
            "type": "object",
            "properties": {
                "variable": {
                    "type": "string"
                    }
                }
        }
        
    |
    """
    # Generates a JSON Schema from a function
    def __get_function_json_schema__(func: FunctionType, ignore: list[str]) -> dict:
        properties: list[str] = []
        # Get the type hints from the function
        type_hints: dict[str, type] = get_type_hints(func)
        defaults: dict[str, Any] = {}
        descriptions: dict[str] = {}
        # If pull_descriptions is true, then pull the descriptions from the functions docstring
        if pull_descriptions:
            descriptions = pull_docstring_parameters(func)
        # For each parameter in the function's signature
        for k, v in inspect.signature(func).parameters.items():
            # Skip the parameter if it's in the ignore list
            if k in ignore:
                continue
            # Add the parameter to the list of properties
            properties.append(k)
            # If a default is provided, set the parameter's default
            if v.default is not inspect.Parameter.empty:
                defaults[k] = v.default
        # Create the JSON Schema with the gathered data
        return create_json_schema(properties=properties, type_hints=type_hints, defaults=defaults, descriptions=descriptions, title=obj.__name__, pull_descriptions=pull_descriptions, pull_required=True)
    
    # Generates a JSON Schema from a model
    def __get_model_json_schema__(model: type) -> dict:
        properties: list[str] = []
        type_hints: dict[str, type] = {}
        defaults: dict[str, Any] = {}
        descriptions: dict[str] = {}
        # If pull_descriptions is true, then pull the descriptions from the functions docstring
        if pull_descriptions:
            descriptions = pull_docstring_parameters(model)
        # This takes a different apporach to the __get_function_json_schema__ function.
        # It makes two passes through the model, once looking at the type hints and
        # a second time looking at the vars. This is how it gets all the data
        # For each type hint in the model
        for k, v in get_type_hints(model).items():
            # Append the property to the list of properties
            properties.append(k)
            # Set the type hint for the property
            type_hints[k] = v
        # For each variable in the model
        for k, v in vars(model).items():
            # If its a private variable (starts with and ends with '__'), then skip it
            if k.startswith("__") and k.endswith("__"):
                continue
            # The variable has a value set, that is going to be used as the default
            defaults[k] = v
            # If the variable isn't in the list of properties yet, append it
            if k not in properties:
                properties.append(k)
            properties.append(k)
        # If no properties were defined, then the object given is cannot be turned into a JSON Schema
        if len(properties) == 0:
            raise InvalidInput("A JSON Schema cannot be generated from the object given")
        return create_json_schema(properties=properties, type_hints=type_hints, defaults=defaults, descriptions=descriptions, title=obj.__name__, pull_descriptions=pull_descriptions, pull_required=True)

    schema: dict = {}
    # Check if the obj is a function
    if type(obj) == FunctionType:
        # If it is, convert the function to a schema
        schema = __get_function_json_schema__(obj, [])
    # If the obj is not a function
    else:
        # Try to get the obj's __init__ function
        init: FunctionType | None = __get_init__(obj)
        # If it has one, use it as the function
        if init:
            schema = __get_function_json_schema__(obj.__init__, ["self"])
        # Otherwise, attempt to treat the object as a model
        else:
            schema = __get_model_json_schema__(obj)
    return schema



def json_call(obj, json: dict, self = None):
    """
    Call a function or initialize an object with the input json as parameters

    This includes additional processing to convert dicts to objects

    :param obj: The function or object to be called or initialized
    :param json: The parameters
    :param self: Optional. Use this if your calling a class method from the class itself and not an initialized object

    Examples:

        class MyClass:
            def __init__(self, my_variable: int) -> None:
                pass

            def my_class_func(self, input_value: int) -> None:
                pass

        # Scenario 1
        # Calling
        json_call(MyClass, {"my_variable": 5})
        # Is the same as
        MyClass(5)

        # Scenario 2
        my_class_obj: MyClass = MyClass(0)
        # Calling
        json_call(MyClass.my_class_func, {"input_value": 5}, my_class_obj)
        # Is the same as
        json_call(my_class_obj.my_class_func, {"input_value": 5})
        # Both are the same as
        my_class_obj.my_class_func(5)


    |
    """
    # If the obj is a method, recall the json_call function passing the individual function and object as self
    if type(obj) == MethodType:
        return json_call(obj.__func__, json, obj.__self__)
    # Start by trying to get the init function from the obj
    func: FunctionType | None = __get_init__(obj)
    # If the obj is a function, then just set func to be the function
    if type(obj) == FunctionType:
        func = obj
    # If the object doesn't have an init function or obj is not a function
    # it cannot be called
    if func == None:
        # Invalid object
        raise Exception()
    # Prepare the data
    molded_data: dict = {}
    # Get the type hints
    type_hints: dict[str, type] = get_type_hints(func)
    # Mold each value
    for key, value in json.items():
        if key not in type_hints:
            raise MissingKey(f"Extra key \033[31m{key}\033[37m not expected in \033[31m{obj}\033[37m")
        molded_data[key] = mold_value(value, type_hints[key])
    if self:
        molded_data["self"] = self
    return obj(**molded_data)