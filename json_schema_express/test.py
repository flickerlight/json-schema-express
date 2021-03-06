import os,sys
import json
import re
from copy import deepcopy
import unittest
from data_producer import DataProducer
from generators import *
from jsonspec.pointer import extract

class TestSchemaParse(unittest.TestCase):
    def test_no_ref(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type":"integer",
            "maximum":5,
            "minimum":1
        }
        dp = DataProducer(schema)
        self.assertEqual(schema,dp.schema)

    def test_internal_single_ref(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "definitions": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street_address": {
                            "type": "string"
                        },
                        "city": {
                            "type": "string"
                        },
                        "state": {
                            "type": "string"
                        }
                    }
                }
            },
            "type": "object",
            "properties": {
                "billing_address": {
                    "$ref": "#/definitions/address"
                }
            }
        }
        new_schema = deepcopy(schema)
        new_schema['properties']['billing_address'] = {
                                                        "type": "object",
                                                        "properties": {
                                                            "street_address": {
                                                                "type": "string"
                                                            },
                                                            "city": {
                                                                "type": "string"
                                                            },
                                                            "state": {
                                                                "type": "string"
                                                            }
                                                        }
                                                    }
        dp = DataProducer(schema)
        self.assertEqual(dp.schema,new_schema)

    def test_internal_multiple_ref(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "definitions": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street_address": {
                            "type": "string"
                        },
                        "code": {
                            "type": "integer"
                        },
                        "state": {
                            "type": "string"
                        }
                    }
                }
            },
            "type": "object",
            "properties": {
                "billing_address": {
                    "$ref": "#/definitions/address/properties/street_address"
                },
                "another_ref":{
                    "$ref": "#/definitions/address/properties/code"
                }
            }
        }
        new_schema = deepcopy(schema)
        new_schema['properties']['billing_address'] = {"type":"string"}
        new_schema['properties']['another_ref'] = {"type":"integer"}
        dp = DataProducer(schema)
        self.assertEqual(dp.schema,new_schema)

    def test_local_file_ref(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "billing_address": { "$ref": "sample_schemas/test_string.json#"}
            }
        }
        dp = DataProducer(schema)
        self.assertEqual(dp.base_dir,'.')
        new_schema = deepcopy(schema)
        new_schema['properties']['billing_address'] = {
                                            "$schema": "http://json-schema.org/draft-04/schema#",
                                            "type":"object",
                                            "properties":{
                                                "patterns":{
                                                    "type": "string",
                                                      "pattern":"[A-Z]{4,10}[0-9]\\.[a-z]{2}"
                                                },
                                                "plains":{
                                                    "type": "string",
                                                      "maxLength":10,
                                                      "minLength":5
                                                }
                                            },
                                            "required":["patterns","plains"]
                                        }
        self.assertEqual(dp.schema,new_schema)

    def test_local_file_ref_specified_path(self):
        self.maxDiff = None
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "billing_address": { "$ref": "test_string.json#"}
            }
        }
        dp = DataProducer(schema,'./sample_schemas')
        new_schema = deepcopy(schema)
        new_schema['properties']['billing_address'] = {
                                            "$schema": "http://json-schema.org/draft-04/schema#",
                                            "type":"object",
                                            "properties":{
                                                "patterns":{
                                                    "type": "string",
                                                      "pattern":"[A-Z]{4,10}[0-9]\\.[a-z]{2}"
                                                },
                                                "plains":{
                                                    "type": "string",
                                                      "maxLength":10,
                                                      "minLength":5
                                                }
                                            },
                                            "required":["patterns","plains"]
                                        }
        self.assertEqual(dp.schema,new_schema)

    def test_remote_url_ref(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema",
            "id":"http://json-schema.org/address",
            "type": "object",
            "properties": {
                "billing_address": { "$ref": "#/properties/extended-address"}
            }
        }
        dp = DataProducer(schema)
        new_schema = deepcopy(schema)  
        new_schema['properties']['billing_address'] = { "type": "string" }
        self.maxDiff = None
        self.assertEqual(dp.schema,new_schema)

    def test_ref_in_definitions(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "definitions": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street_address": {
                             "$ref": "test_string.json#"
                         },
                        "code": {
                            "type": "integer"
                        }
                    }
                }
            },
            "type": "object",
            "properties": {
                "billing_address": {
                    "$ref": "#/definitions/address/properties/street_address"
                },
                "another_ref":{
                    "$ref": "#/definitions/address/properties/code"
                }
            },
                "required":["billing_address","another_ref"]
        }
        dp = DataProducer(schema,'./sample_schemas')
        self.assertEqual(dp.schema['definitions']['address'],{
                                                        "type": "object", 
                                                        "properties": {
                                                            "code": {
                                                                "type": "integer"
                                                            }, 
                                                            "street_address": {
                                                                "$schema": "http://json-schema.org/draft-04/schema#", 
                                                                "required": [
                                                                    "patterns", 
                                                                    "plains"
                                                                ], 
                                                                "type": "object", 
                                                                "properties": {
                                                                    "patterns": {
                                                                        "pattern": "[A-Z]{4,10}[0-9]\\.[a-z]{2}", 
                                                                        "type": "string"
                                                                    }, 
                                                                    "plains": {
                                                                        "minLength": 5, 
                                                                        "type": "string", 
                                                                        "maxLength": 10
                                                                    }
                                                              }
                                                            }
                                                        }
                                                    })
        value = dp.produce()
        self.assertEqual(len(value),2)
        self.assertEqual(len(value['billing_address']),2)
        self.assertTrue(isinstance(value['billing_address']['patterns'],basestring))
        self.assertTrue(isinstance(value['billing_address']['plains'],basestring))
        self.assertTrue(isinstance(value['another_ref'],int))

class TestDataGenerate(unittest.TestCase):

    def test_single_key_standard_generator(self):
        schema = {
                "type":"integer",
                "maximum":5,
                "minimum":1
          }
        dp = DataProducer(schema)
        self.assertEqual(dp.generator_cache,{})
        self.assertIn(dp.produce(),range(1,6))
        self.assertTrue(isinstance(dp.generator_cache['root'],StdIntegerRandom))
        current_generator_id = id(dp.generator_cache['root'])
        for i in range(0,5):
            value = dp.produce()
            self.assertIn(value,range(1,6))
            self.assertEqual(len(dp.generator_cache),1)
            self.assertEqual(current_generator_id,id(dp.generator_cache['root']))

    def test_single_key_other_generator_in_schema(self):
        schema ={
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "integer",
                "_generator_config": {
                    "start": 0,
                    "step": 100,
                    "generator": "StdIntegerSequence"
                    }
                }
        dp = DataProducer(schema)
        for i in range(0,5):
            self.assertEqual(dp.produce(),i*100)
            self.assertTrue(isinstance(dp.generator_cache['root'],StdIntegerSequence))
            
    def test_single_key_other_generator_in_init(self):
        schema ={
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "integer",
                "_generator_config": {
                    "start": 0,
                    "step": 100
                    }
                }
        dp = DataProducer(schema,generator_mapping = {"integer":"StdIntegerSequence"})
        for i in range(0,5):
            self.assertEqual(dp.produce(),i*100)
            self.assertTrue(isinstance(dp.generator_cache['root'],StdIntegerSequence))

    def test_muliple_simple_keys_in_one_object(self):
        schema = { 
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "int_a": {
                  "type": "integer",
                  "maximum": 50,
                  "minimum": 20,
                  "multipleof": 4
                },
                "float_b": {
                  "type": "number",
                  "maximum": 100.5,
                  "minimum": 10.5
                },
                "string_c": {
                  "type": "string",
                  "maxLength": 15
                },
                "bool_d": {
                  "type": "boolean"
                },
                "null_e":{
                    "type":"null"
                }
            },
            "required":["int_a","float_b","string_c","bool_d","null_e"]
        }

        dp = DataProducer(schema)
        result = dp.produce() 
        self.assertIn(result['int_a'],range(20,51))
        self.assertEqual(result['int_a'] % 4,0) 
        self.assertTrue(result['float_b'] <= 100.5)
        self.assertTrue(result['float_b'] % 10.5,0.0)
        self.assertIn(len(result['string_c']),range(0,16))
        self.assertIn(result['bool_d'],(True,False))
        self.assertEqual(result['null_e'],None)
        #type null doesn't need generator
        self.assertEqual(len(dp.generator_cache),4)
        self.assertTrue(isinstance(dp.generator_cache['root.int_a'],StdIntegerRandom))
        self.assertTrue(isinstance(dp.generator_cache['root.float_b'],StdNumberRandom))
        self.assertTrue(isinstance(dp.generator_cache['root.string_c'],StdStringRandom))
        self.assertTrue(isinstance(dp.generator_cache['root.bool_d'],StdBooleanRandom))

    def test_array_list(self):
        schema = {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "array",
                "maxItems":7,
                "minItems":2,
                "items": {
                    "type": "integer",
                    "maximum": 33,
                    "minimum": 15
                },
                "uniqueItems":True
            }
        dp = DataProducer(schema)
        value = dp.produce()
        self.assertTrue(isinstance(dp.generator_cache['root.integer'],StdIntegerRandom))
        self.assertIn(len(value),range(2,8))
        for v in value:
            self.assertIn(v,range(15,34))
        self.assertTrue(len(value) == len(set(value)))
        
    def test_array_tuple(self):
        schema = {
            "type": "array",
            "items": [
                {
                  "type": "number"
                },
                {
                  "type": "string"
                }
            ]
        }
        dp = DataProducer(schema)
        value = dp.produce()
        self.assertTrue(len(value),2)
        self.assertTrue(isinstance(value[0],float))
        self.assertTrue(isinstance(value[1],basestring))

    def test_array_nested(self):
        schema = {
            "type": "array",
            "items": [
                {
                    "type": "number"
                }, 
                {
                    "type": "string"
                }, 
                {
                    "type": "array",
                    "items": {
                        "type": "boolean"
                    }
                }
            ]
        }
        dp = DataProducer(schema)
        value = dp.produce()
        self.assertTrue(isinstance(value,list))
        self.assertEqual(len(value),3)
        self.assertTrue(isinstance(value[2],list))
        self.assertIn(len(value[2]),range(1,11))

    def test_object_nested(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
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
                        "inner_string_c": {
                            "type": "string",
                            "maxLength": 15
                        },
                        "inner_bool_d": {
                            "type": "boolean"
                        }
                    },
                    "required":["inner_bool_d","inner_string_c"]
                }
            },
            "required":["outer_int_a","inner_object"]
        }
        dp =  DataProducer(schema)
        value = dp.produce()
        self.assertIn(value['outer_int_a'],range(20,51))
        self.assertTrue(value['outer_int_a']%4 == 0)
        self.assertIn(value['inner_object']['inner_bool_d'],(True,False))
        self.assertTrue(isinstance(value['inner_object']['inner_string_c'],basestring))
        self.assertTrue(len(value['inner_object']['inner_string_c']) <= 15)
        self.assertEqual(len(value['inner_object']),2)
        self.assertEqual(len(value),2)

    def test_null(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "null"
        }
        dp = DataProducer(schema)
        self.assertEqual(dp.produce(),None)

    def test_format(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "ipv4": {
                    "type": "string",
                    "format": "ipv4"
                }
            },
            "required":["ipv4"]
        }
        dp = DataProducer(schema)
        value = dp.produce()
        pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        self.assertEqual(len(value),1)
        self.assertTrue(pat.match(value['ipv4']))

    def test_produce_list_default_length(self):
        schema = {
            "type":"integer",
            "maximum":5,
            "minimum":1
        }
        dp = DataProducer(schema)
        results = dp.produce_list()
        self.assertTrue(isinstance(results,list))
        self.assertEqual(len(results),10)
        self.assertIn(results[0],range(1,6))

    def test_produce_list(self):
        schema = {
            "type":"integer",
            "maximum":5,
            "minimum":1
        }
        dp = DataProducer(schema)
        results = dp.produce_list(5)
        self.assertEqual(len(results),5)

    def test_produce_list_illegal_length(self):
        schema = {
            "type":"integer"
        }
        dp = DataProducer(schema)
        self.assertEqual(dp.produce_list('a'),[])

    def test_partly_required(self):
        schema = {
            "type":"object",
            "properties":{
                "int_a":{
                    "type":"integer",
                    "maximum":9,
                    "minimum":4
                },
                "string_b":{
                    "type":"string",
                    "maxLength":6,
                    "minLength":3
                }
            },
            "required":["int_a"]
        }
        dp = DataProducer(schema)
        b_no_present = b_present = False
        while not (b_no_present and b_present):
            value = dp.produce()
            self.assertIn(value['int_a'],range(4,10))
            if 'string_b' in value:
                self.assertTrue(isinstance(value['string_b'],basestring))
                self.assertIn(len(value['string_b']),range(3,7))
                b_present = True
            else:
                b_no_present = True

    def test_no_required_default(self):
        '''If "required" is not presented in the schema, the default behavior is that every key 
        will be regarded as non-required'''
        schema = {
            "type":"object",
            "properties":{
                "int_a":{
                    "type":"integer",
                    "maximum":9,
                    "minimum":4
                },
                "string_b":{
                    "type":"string",
                    "maxLength":6,
                    "minLength":3
                }
            }
        }
        dp = DataProducer(schema)
        a_present = a_no_present = b_no_present = b_present = False
        while not (a_present and a_no_present and b_no_present and b_present):
            value = dp.produce()
            if 'int_a' in value:
                self.assertIn(value['int_a'],range(4,10))
                a_present = True
            else:
                a_no_present = True
            if 'string_b' in value:
                self.assertTrue(isinstance(value['string_b'],basestring))
                self.assertIn(len(value['string_b']),range(3,7))
                b_present = True
            else:
                b_no_present = True

def Data_Suite():
    ts =unittest.TestSuite()
    #ts.addTest(unittest.makeSuite(TestInteger))
    #ts.addTest(unittest.makeSuite(TestFloat))
    ts.addTest(unittest.makeSuite(TestSchemaParse))
    ts.addTest(unittest.makeSuite(TestDataGenerate))
    return ts

if __name__ == '__main__':
    mySuit = Data_Suite()
    runner = unittest.TextTestRunner()
    runner.run(mySuit)


