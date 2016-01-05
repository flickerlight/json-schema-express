# json-schema-express
json-schema-express is a a Python library to help generate random data according to a given json schema. By default it provides random generators for json values, you can also write your own generator and specify it to use.

## Example
### Default Generator
By default, json-schema-express uses default generators in generators/std directory to generate value for each json type. Default mapping is as following:

    "number":"std_number_generator.StdNumberRandom",
    "boolean":"std_boolean_generator.StdBooleanRandom",
    "integer":"std_integer_generator.StdIntegerRandom",
    "string":"std_string_generator.StdStringRandom"

Here is an example of generating a nested json object:
```python
import json
from json_schema_express import DataProducer

schema = '''{
    "type": "object",
    "properties": {
        "outer_int_a": {
            "type": "integer",
            "maximum": 50,
            "minimum": 20,
            "multipleof": 4
        },
        "inner_object": {
            "type": "object",
            "properties": {
                "inner_string_b": {
                    "type": "string",
                    "maxLength": 15,
                    "pattern": "[A-Z]{4,10}[0-9]\\\\.[a-z]{2}"
                },
                "inner_bool_c": {
                    "type": "boolean"
                }
            }
        }
    }
}'''
dp = DataProducer(schema)
for i in range(0,2):
    print json.dumps(dp.produce(),indent=4,sort_keys=True)
```
The output might be like:
```
{
    "inner_object": {
        "inner_bool_c": true, 
        "inner_string_b": "ERMGS6.tg"
    }, 
    "outer_int_a": 24
}
{
    "inner_object": {
        "inner_bool_c": false, 
        "inner_string_b": "WI91.oe"
    }, 
    "outer_int_a": 32
}
```

### Specify non-default generator
There are two ways to specify non-default generator to use:

1. You can change the generator for a specified key by setting '__generator' key in the json schema. Only this key will be genreated by the specified generator. Other keys of the same type are not affected.
2. You can pass a config dictionary to the DataProducer() constructor to overwritten the default setting. Notice that in this way, all keys of the same type will be genereted by the specified generator.

For example, in std_integer_generator we provide a class StdIntegerSequence to output a consecutive integer sequence. Both below code blocks achieve the same goal:

```python
from json_schema_express import DataProducer

schema = '''{
    "type": "integer",
    "__start":0,
    "__step":100,
    "__generator":"std_integer_generator.StdIntegerSequence"
    }'''
#"__start" and "__step" are parameters required by StdIntegerSequence.
#We add "__" prefix to differentiate with standard json schema keywords.
#But "__" is not required.
dp = DataProducer(schema)
for i in range(0,5):
    print dp.produce()
```

```python
from json_schema_express import DataProducer
schema = '''{
    "type": "integer",
    "__start":0, 
    "__step":100
    }'''
dp = DataProducer(schema,{"integer":"std_integer_generator.StdIntegerSequence"})
for i in range(0,5):
    print dp.produce()
```
Both the outputs are:
```
0
100
200
300
400
```
# Write your own generator
All generators are placed in the generators directory. We provide some standard generators in the std sub-directory. 

You can define your own generator following the std_ examples. The important things are:

1. Your generator class need to accept the key's json schema in its __init__() method, and provides a generate() method to return the generated value.

2. Once a generator is instantialized for a json key, this generator instance will be associated with the key and cached by DataProducer. Next time DataProducer meets the key, it will directly call the cached instance to get the value. This is how we generate integer sequence. 

## Json Schema Keywords Supported
json-schema-express now supports below json schema keywords: 
* Json Type

string, number(float acutally), integer, boolean, object, array

* Type-Speicific Keywords
    
    - number/integer
    
    maximum, minimum, exclusiveMaximum, exlculisveMinimum, mulitpleof

    - string
    
    minLength, maxLength, pattern 

    - object
    
    properties

    - array
    
    items, minItems, maxItems, uniqueItems
* Generic Keywords
    - enum
    
    It should be used together with type string/integer/number, standalone usage is not supported.

## Json Schema Keywords NOT Currently Supported

- format
- required
- anyof
- oneof
- allof
- definitions and $ref




