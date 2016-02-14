# json-schema-express
json-schema-express is a a Python library to help generate random/certain pattern data according to a given [json schema](http://json-schema.org/) (for fuziing testing purpose, e.g.). By default this libary provides random generators for json values, you can also write your own generator and specify it to use.

json-schema-express supports Python 2.6+ and requires below non-standard python libraries:

- [jsonschema](https://github.com/Julian/jsonschema)
- [jsonspec](https://github.com/johnnoone/json-spec)
- [rstr](https://pypi.python.org/pypi/rstr/2.1.3)
- [faker](https://github.com/joke2k/faker)

Currently json-schema-express only supports json schema draft version 4. Hypermedia schema and version 3 support is still on the way.

## Example
Here is a basic example to generate random data for a given json schema:
```python
import json
from json_schema_express import DataProducer

schema = {
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
}
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

## Generators
json-schema-express main process loads a bunch of generators to generate random data for each json key. You can easily change the correspondece between genrators and json keys, as well as create and plug-in customized generators.

### Default Generators
By default, json-schema-express uses default generators for each json type/format. The mapping is set in the \_\_init\_\_()
 method of DataProducer class in **data_producer.py**:
```python
...
self.type_vs_generator = {
            "number":"StdNumberRandom",
            "boolean":"StdBooleanRandom",
            "integer":"StdIntegerRandom",
            "string":"StdStringRandom",
            "date-time":"StdDateTimeRandom",
            "email":"StdEmailRandom",
            "ipv4":"StdIPv4Random",
            "ipv6":"StdIPv6Random",
            "uri":"StdURIRandom",
            "hostname":"StdDomainNameRandom"
        }
```
All default generators are imported from **generators.py**.

### Customize generator
Often you may want to generate more than simple random data, such as the integer sequence we exhibited above. In this case, you can write your own generators.

All existing generators are placed in **generators.py**. Customized generator class can be defined following these examples. New generators can be put in generator.py or any other python file. In the latter case, your generator class has to be imported when use DataProducer. Below are the common things you need to know:

1. Your generator class needs to accept a json schema in its \_\_init\_\_() method, and provides a generate() method to return the generated value. You can require the json schema to provide additional parameters in object _generator_config.

2. A generator is instantialized when DataProducer meets a json key for the first time, and this generator instance will be associated with the key and cached.Next time DataProducer meets the key, it will directly call the cached instance to return the value. In this way you can save any intemediate status/parameters in your generator instance and reuse them in the future. 

Here is the example of a simple customized generator StdIntegerSequence:

```python
class StdIntegerSequence:
    '''Define an integer sequence with specified start and step parameters, and return one element each time when generate() is called'''
    def __init__(self,config):
        self.start = config['_generator_config']['start']
        self.step = config['_generator_config']['step']
        self.current = self.start-self.step

    def generate(self):
        self.current +=self.step
        return self.current
```
### Specify Generator to Use
There are two ways to specify a generator into use:

1. You can assign a generator for a specific key by setting '_generator_config' in the json schema. Only this key will be genreated by the assigned generator, other keys of the same type are not affected.

2. You can pass a config dictionary to the DataProducer() constructor to overwritten the default setting. Notice that in this way, all keys of the same type will be genereted by the specified generator.

For example, in previous section we provide a custom class StdIntegerSequence to output a consecutive integer sequence. Both below code blocks make use of this generator:

```python
#Define generator in _generator_config
from json_schema_express import DataProducer

schema = {
  "type": "integer",
  "_generator_config": {
    "start": 0,
    "step": 100,
    "generator": "StdIntegerSequence"
  }
}
#"start" and "step" are parameters required by StdIntegerSequence.
dp = DataProducer(schema)
for i in range(0,5):
    print dp.produce()
```

```python
#override the tye_vs_generator setting
from json_schema_express import DataProducer
schema = {
    "type": "integer",
    "_generator_config": {
        "start": 0,
        "step": 100
        }
    }
dp = DataProducer(schema,{"integer":"StdIntegerSequence"})
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

## Supported and Unsupported Json Schema Keywords

### Supported
Currently json-schema-express supports below json schema keywords: 

#### Type

Json-schema-express currently only support single value of "type" keyword, including string, number(implemented as float), integer, boolean, object and array.
The "enum" types (such as [string, integer]) are not supported.

#### Generic Keywords

- enum
    
It should be used together with type string/integer/number, standalone usage is not supported.

- $ref
    
Currently only support one level $ref, nested $ref (i.e., there are further $ref(s) in the referred json) is not supported.


#### Type-Speicific Keywords

* number and string

Support of these keywords are implemented in corresponding standard generator classes.If you write your own generator, you need to deal with these keywords by your own.

- number/integer
    
maximum, minimum, exclusiveMaximum, exlculisveMinimum, mulitpleof

- string
    
minLength, maxLength, pattern, format(ipv4/ipv6/email/uri/hostname/date-time)

* object and array

- object
    
properties, required (Keys that are not required will randomly appear in the generated json.)

- array
    
items, minItems, maxItems, uniqueItems
    
### Unsupported

- MaxProperties, MinProperties, AdditionalProperties, patternProperties
- anyof, oneof, allof
- not
- dependencies




