# doms-json

[![PyPI](https://img.shields.io/pypi/v/doms-json.svg)](https://pypi.org/project/doms-json/)
[![Tests](https://github.com/DominicDJC/doms-json/actions/workflows/test.yml/badge.svg)](https://github.com/DominicDJC/doms-json/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/DominicDJC/doms-json?include_prereleases&label=changelog)](https://github.com/DominicDJC/doms-json/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/DominicDJC/doms-json/blob/main/LICENSE)

A JSON toolkit that's particularly useful for what I'm making

# Installation

Install this library using `pip`:
```bash
pip install doms-json
```
# Usage

I have a few projects in which I needed to do the same things, so I figured I'd make it a package. That's what this is.

Some key functionality within this package includes:
- Creating JSON Schemas
- Describing JSON schemas
- Pulling parameter descriptions from docstrings
- Generating JSON schemas from functions and objects
   - With descriptions pulled from docstrings
- Calling functions or initializing objects with a dictionary input

## Creating a JSON schema

```python
def create_json_schema(properties: list[str],
                       type_hints: dict[str, type] | None = None,
                       defaults: dict[str, Any] | None = None,
                       descriptions: dict[str, str]| None = None,
                       title: str | None = None,
                       pull_descriptions: bool = False) -> dict:
```

The only thing required to create a JSON schema using the ```create_json_schema``` function is a list of properties.

For example: 
```python
create_json_schema(["my_variable", "my_second_variable"])
```
Will generate the following JSON schema:

```python
{
    "type": "object",
    "properties": {
        "my_variable": { },
        "my_second_variable": { }
    }
}
```

This is likely not very usefully. In most cases, you'll probably need to define types, defaults, descriptions, or a title.

### Defining Types

Given the previous example, to define types for the variables we'll need to create a dictionary defining them:

```python
types: dict = {
    "my_variable": str,
    "my_second_variable": int
}
```

Let's pass this into the function:
```python
create_json_schema(["my_variable", "my_second_variable"], types)
```
The schema will now be generate as follows:

```python
{
    "type": "object",
    "properties": {
        "my_variable": {
            "type": "string"
        },
        "my_second_variable": {
            "type": "integer"
        }
    }
}
```

### Setting Defaults

In some scenarios, you may want to define default values. These are handled similarly to how types are defined. We need to create a dictionary defining them:

```python
defaults: dict = {
    "my_variable": "Hello world!"
}
```

Pass it into the function:
```python
create_json_schema(["my_variable", "my_second_variable"], types, defaults)
```
Now it will generate with both types and defaults:

```python
{
    "type": "object",
    "properties": {
        "my_variable": {
            "type": "string",
            "default": "Hello world!"
        },
        "my_second_variable": {
            "type": "integer"
        }
    }
}
```

### Adding Descriptions

Descriptions work the same way as setting types and defaults, we need to define them:

```python
descriptions: dict = {
    "my_second_variable": "The number of lines of code"
}
```

Call the function:
```python
create_json_schema(["my_variable", "my_second_variable"], types, defaults, descriptions)
```
And now it will be generated with types, defaults, and descriptions:

```python
{
    "type": "object",
    "properties": {
        "my_variable": {
            "type": "string",
            "default": "Hello world!"
        },
        "my_second_variable": {
            "type": "integer",
            "description": "The number of lines of code"
        }
    }
}
```

### Setting Requirements

To require variables in the JSON schema, all you have to do is pass a list of the required variables: 
```python
create_json_schema(["my_variable", "my_second_variable"], types, defaults, descriptions, ["my_variable"])
```
The schema will now include the requirements:

```python
{
    "type": "object",
    "properties": {
        "my_variable": {
            "type": "string",
            "default": "Hello world!"
        },
        "my_second_variable": {
            "type": "integer",
            "description": "The number of lines of code"
        }
    },
    "required": ["my_variable"]
}
```

### Setting a Title

In some case, you may want to set a title for the JSON schema. All you have to do is pass it in the function:
```python
create_json_schema(["my_variable", "my_second_variable"], types, defaults, descriptions, ["my_variable"], "MySchema")
```
This will add the title to the schema:

```python
{
    "type": "object",
    "title": "MySchema",
    "properties": {
        "my_variable": {
            "type": "string",
            "default": "Hello world!"
        },
        "my_second_variable": {
            "type": "integer",
            "description": "The number of lines of code"
        }
    },
    "required": ["my_variable"]
}
```

All of these can be used interchangeably. For example:
- ```create_json_schema(["my_variable", "my_second_variable"], type_hints=types, required=["my_variable"])```
- ```create_json_schema(["my_variable", "my_second_variable"], defaults=defaults, descriptions=descriptions)```
- ```create_json_schema(["my_variable", "my_second_variable"], title="MySchema", type_hints=types)```

## Making Things Easier

In some cases, you may need to have a property is that is not a primative or array. You may need an object. Objects can significantly increase the complexity in terms of both creating and handling JSON schemas. Let's look at this example:

```python
class MyObject:
    def __init__(self, my_variable: str, my_second_variable: int) -> None:
        self.my_variable: str = my_variable
        self.my_second_variable: int = my_second_variable
```

The JSON schema for this object would be:

```python
{
    "type": "object",
    "title": "MyObject",
    "properties": {
        "my_variable": {
            "type": "string"
        },
        "my_second_variable": {
            "type": "integer"
        }
    },
    "required": ["my_variable", "my_second_variable"]
}
```

### Generating From Functions or Objects

Instead of using the ```create_json_schema``` to create a schema for this object manually, the ```generate_json_schema``` function will do it automatically:

```python
generate_json_schema(MyObject)
```

This will generate the same exact JSON schema shown previously.

It checks for types, defaults and pulls the title automatically. Let's say ```my_variable``` should default to ```"Hello world!"```:

It also works with functions

```python
def my_function(int_variable: int | None, str_variable: str = "This is a string"):...

generate_json_schema(my_function)
```

Notice the type given for ```int_variable```: ```int | None```. Specifying that a property can be ```None``` dictates that that property is not required.

```python
{
    "type": "object",
    "title": "my_function",
    "properties": {
        "int_variable": {
            "type": "integer"
        },
        "str_variable": {
            "type": "string",
            "default": "This is a string"
        }
    },
    "required": ["str_variable"]
}
```

And it works with class using class variables

```python
class MyClass:
    names: list[str]

generate_json_schema(MyClass)
```

```python
{
    "type": "object",
    "title": "MyClass",
    "properties": {
        "names": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["names"]
}
```

### Using Docstrings

With docstrings, you can easily create definitions for functions and objects with parameter defintions in the reStructuredText (reST) format:

```:param variable: Variable description```

```python
class MyObject:
    def __init__(self, my_variable: str) -> None:
        """
        :param my_variable: A simple string variable
        """
        self.my_variable: str = my_variable
```

When calling ```generate_json_schema(MyObject)```, we'll end up with the following JSON schema:

```python
{
    "type": "object",
    "title": "MyObject",
    "properties": {
        "my_variable": {
            "type": "string",
            "description": "A simple string variable"
        }
    },
    "required": ["my_variable"]
}
```

When using the ```generate_json_schema``` function, ```pull_descriptions``` is enabled. If this is disabled, the generation will ignore any docstrings.

This functionality is also available in the ```create_json_schema``` function, though it is disabled by default.

If for some reason you just need to retrieve the parameter descriptions from a function or object's docstring, you can use the ```pull_docstring_parameters``` function

### Manually Describing a JSON Schema

If you already have a JSON schema and you need to add descriptions, use the ```describe_json_schema``` function to created a described copy of your schema.

```python
{
    "type": "object",
    "properties": {
        "my_object": {
            "type": "object",
            "properties": {
                "my_string": {
                    "type": "string"
                }
            }
        },
        "my_number": {
            "type": "integer"
        }
    }
}
```

To describe ```"my_object"``` and ```"my_number"```:

```python
{
    "my_object": "An object",
    "my_number": "An integer"
}
```

Describing a property that belongs to an object requires some more formating. To describe ```"my_string"``` and ```"my_number"```:

```python
{
    "my_object": {
        "my_string": "A string"
    },
    "my_number": "An integer"
}
```

If you want to describe the propertys within an object and the object itself, you'll need to use the ```"properties"``` and ```"description"``` keywords. To describe ```"my_object"```, ```"my_string"```, and ```"my_number"```

```python
{
    "my_object": {
        "properties": {
            "my_string": "A string"
        }
        "description": "An object"
    },
    "my_number": "An integer"
}
```

### Convert a type to a JSON Schema Type

The ```to_json_schema_type``` function can be used to convert a type, union, tuple of types, or list of types into a JSON Schema type:

```python
to_json_schema_type(str)
```
Returns
```python
JSONSchemaType(
    schema_type={"type": "string"},
    requried=True
)
```

It can also handle objects, automatically generating JSON schemas if necessary. Enable ```pull_descriptions``` to pull the descriptions from docstrings.

If you want the basic type, use the ```to_direct_json_schema_type```

```python
to_direct_json_schema_type(str) == "string"
```

## Calling Functions

Being able to call a function or initialize an object using a dictionary with the values can be useful. The ```json_call``` function simplifies the process significantly. For example:

```python
def get_weather(date: str, city: str, state: str):...
```

Say the ```generate_json_schema``` function was used to generate a ```get_weather``` tool for an LLM. The LLM will respond with a JSON response of parameters to use with the function:

```python
llm_response = {
    "date": "2025-01-01",
    "city": "Dallas",
    "state": "Texas"
}
```

Passing this along with the ```get_weather``` function will call properly assign the data and call the function

```python
json_call(get_weather, llm_response)
```

It also handles objects:

```python
class Location:
    def __init__(self, city: str, state: str) -> None:
        self.city: str = city
        self.state: str = state


def get_weather(date: str, location: Location):...
```

When used with an LLM, you'll get a response like this:

```python
{
    "date": "2025-01-01",
    "location": {
        "city": "Dallas",
        "state": "Texas"
    }
}
```

The ```json_call``` function will automatically initialize a ```Location``` object from the given ```"location"``` data.

If the ```"location"``` value was already a ```Location``` object, then it will pass the data as is.

The ```json_call``` function handles type conversions to ensure that the function is called with the expected types.

## Molding Values

The ```json_call``` function is built upon another useful function: ```mold_value```

The ```mold_value``` function takes in a ```value``` and a ```expected_type```, then converts the value to the expected type:

```python
class Location:
    def __init__(self, city: str, state: str) -> None:
        self.city: str = city
        self.state: str = state

data = {"city": "Dallas", "state": "Texas"}

# Mold the data into a Location object
location_object: Location = mold_value(data, Location)
```

It works with many different types, with support for **Unions** and typed **Lists**:

```python
data = [100, "string", 0.25, {"city": "Dallas", "state": "Texas"}]

# The 100, "string", and 0.25 will be uneffected, while the 
# location data will be converted to a Location object
molded_data = mold_value(data, list[int | str | float | Location])
```

# Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd doms-json
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
