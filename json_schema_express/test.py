import os,sys
import json
from copy import deepcopy
import unittest
from data_producer import DataProducer
from generators import *
from jsonspec.pointer import extract

class TestInteger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "integer",
            "minimum": 0,
            "maximum": 2
        }

    def test_random_range(self):
        dp=DataProducer(self.original_schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),range(self.original_schema['minimum'],self.original_schema['maximum']+1))

    def test_multipleof_positive(self):
        schema=deepcopy(self.original_schema)
        schema['multipleof']=5
        schema['minimum']=1
        schema['maximum']=20
        dp=DataProducer(schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),range(5,21,5))

    def test_multipleof_negative(self):
        schema=deepcopy(self.original_schema)
        schema['multipleof']=-5
        schema['minimum']=1
        schema['maximum']=20
        dp=DataProducer(schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),range(5,21,5))

    def test_exclusive_max(self):
        schema=deepcopy(self.original_schema)
        schema['exclusivemaximum']=True
        schema['minimum']=1
        schema['maximum']=2
        dp=DataProducer(schema)
        for i in range(0,5):
            self.assertEqual(dp.produce(),1)

    def test_exclusive_min(self):
        schema=deepcopy(self.original_schema)
        schema['exclusiveminimum']=True
        schema['minimum']=1
        schema['maximum']=2
        dp=DataProducer(schema)
        for i in range(0,5):
            self.assertEqual(dp.produce(),2)

    def test_no_border(self):
        schema=deepcopy(self.original_schema)
        schema.pop('minimum',None)
        schema.pop('maximum',None)
        dp=DataProducer(schema)
        for i in range(0,5):
            value=dp.produce()
            self.assertTrue(value>-sys.maxint-1)
            self.assertTrue(value<sys.maxint)

    def test_enum(self):
        schema=deepcopy(self.original_schema)
        schema['enum']=[34,15,52]
        dp=DataProducer(schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),[34,15,52])

    def test_sequence(self):
        schema = json.loads(open('./sample_schemas/test_integer_sequence.json','rb').read())
        dp=DataProducer(schema)
        for i in range(0,5):
            self.assertEqual(dp.produce(),i*100)


class TestFloat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type":"number"
        }

    def test_random_range(self):
        schema=deepcopy(self.original_schema)
        schema['maximum']=5.0
        schema['minimum']=1.0
        dp=DataProducer(schema)
        for i in range(0,5):
            value=dp.produce()
            self.assertTrue(value>=1.0)
            self.assertTrue(value<=5.0)

class TestSchemaParse(unittest.TestCase):
    def test_no_ref(self):
        schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type":"integer",
            "maximum":5,
            "minimum":1
        }
        dp=DataProducer(schema)
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
        new_schema['properties']['billing_address']={
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
        new_schema['properties']['billing_address']={"type":"string"}
        new_schema['properties']['another_ref']={"type":"integer"}
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
        new_schema=deepcopy(schema)
        new_schema['properties']['billing_address']={
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
                                            }
                                        }
        self.assertEqual(dp.schema,new_schema)

    def test_local_file_ref_specified_path(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "billing_address": { "$ref": "test_string.json#"}
            }
        }
        dp = DataProducer(schema,'./sample_schemas')
        new_schema=deepcopy(schema)
        new_schema['properties']['billing_address']={
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
                                            }
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
        new_schema['properties']['billing_address']= { "type": "string" }
        self.maxDiff = None
        self.assertEqual(dp.schema,new_schema)


class TestDataGenerate(unittest.TestCase):
    def test_single_key_standard_generator(self):
        schema={
                "type":"integer",
                "maximum":5,
                "minimum":1
          }
        dp=DataProducer(schema)
        self.assertEqual(dp.generator_cache,{})
        self.assertIn(dp.produce(),range(1,6))
        self.assertTrue(isinstance(dp.generator_cache['root'],StdIntegerRandom))
        current_generator_id=id(dp.generator_cache['root'])
        for i in range(0,5):
            value=dp.produce()
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
        dp=DataProducer(schema,generator_mapping={"integer":"StdIntegerSequence"})
        for i in range(0,5):
            self.assertEqual(dp.produce(),i*100)
            self.assertTrue(isinstance(dp.generator_cache['root'],StdIntegerSequence))

    def test_muliple_simple_keys_in_one_object(self):
        schema={
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
            }
        }

        dp=DataProducer(schema)
        result=dp.produce() 
        self.assertIn(result['int_a'],range(20,51))
        self.assertEqual(result['int_a']%4,0) 
        self.assertTrue(result['float_b']<=100.5)
        self.assertTrue(result['float_b']%10.5,0.0)
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
        schema={
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
        dp=DataProducer(schema)
        value=dp.produce()
        self.assertTrue(isinstance(dp.generator_cache['root.integer'],StdIntegerRandom))
        self.assertIn(len(value),range(2,8))
        for v in value:
            self.assertIn(v,range(15,34))
        self.assertTrue(len(value)==len(set(value)))
        

    def test_array_tuple(self):
        schema={
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
        dp=DataProducer(schema)
        value=dp.produce()
        self.assertTrue(len(value),2)
        self.assertTrue(isinstance(value[0],float))
        self.assertTrue(isinstance(value[1],basestring))

def Data_Suite():
    ts =unittest.TestSuite()
    #ts.addTest(unittest.makeSuite(TestInteger))
    #ts.addTest(unittest.makeSuite(TestFloat))
    #ts.addTest(unittest.makeSuite(TestSchemaParse))
    ts.addTest(unittest.makeSuite(TestDataGenerate))
    return ts


if __name__=='__main__':
    mySuit = Data_Suite()
    runner = unittest.TextTestRunner()
    runner.run(mySuit)


