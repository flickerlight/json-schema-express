#!/usr/bin/env python

import json
import sys
import os
import random
from jsonschema import Draft4Validator
from generators import *


class DataProducer:
    def __init__(self,schema,plugin_config=None):
        self.schema=schema
        self.plugin_cache={}
        self.object_defines={}
        self.type_vs_plugin={
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
        if plugin_config:
            for key,value in plugin_config.items():
                self.type_vs_plugin[key]=value
        self._parse_schema()

    def _parse_schema(self):
        Draft4Validator.check_schema(self.schema)
        self.object_defines['root']=self.schema
        #save all definitions for future refererence
        if 'definitions' in self.schema:
            for key, value in self.schema['definitions'].items():
                self.object_defines[key]=value

    def produce(self):
        return self.build_object('root',self.object_defines['root'])

    def build_object(self,obj_key,obj_def):
        if "$ref" in obj_def:
            ref_def = obj_def['$ref'].split('/')[-1]
            return self.build_object(obj_key, self.object_defines[ref_def])
        elif obj_def['type'] == 'object':
            result_object={}
            for key, definition in obj_def['properties'].items():
                prop_key = obj_key+'.'+key
                result_object[key] = self.build_object(prop_key,definition)
            return result_object
        elif obj_def['type'] in ['string','integer','number','boolean']:
            return self.build_value(obj_key,obj_def)
        elif obj_def['type'] == 'array':
            return self.build_array(obj_key,obj_def)
        elif obj_def['type'] == 'null':
            return None
        else:
            raise ValueError('Unsupported value for object type: '+obj_def['type'])

    def build_value(self,obj_key,obj_def):
        if '_generator_config' not in obj_def or 'generator' not in obj_def['_generator_config']:
            if 'format' in obj_def.keys():
                #get generator according to the format
                generator = self.get_generator(obj_key, self.type_vs_plugin[obj_def['format']],obj_def)
            else:
                generator = self.get_generator(obj_key,self.type_vs_plugin[obj_def['type']],obj_def)
        else:
            generator = self.get_generator(obj_key,obj_def['_generator_config']['generator'],obj_def)
        return generator.generate()

    def build_array(self,obj_key,obj_def):
        result_array = []
        if 'minItems' in obj_def:
            self.minLength = obj_def['minItems']
        else:
            self.minLength = 1
        if 'maxItems' in obj_def:
            self.maxLength = obj_def['maxItems']
        else:
            self.maxLength = 10
        if 'uniqueItems' in obj_def:
            self.uniqueItems = obj_def['uniqueItems']
        else:
            self.uniqueItems = False

        if isinstance(obj_def['items'],list):
            for i in range(0,len(obj_def['items'])):
                prop_key = obj_key+'.'+str(i)
                result_array.append(self.build_object(prop_key, obj_def['items'][i]))
        else:
            actual_number = random.randrange(self.minLength,self.maxLength+1)
            prop_key = obj_key+'.'+obj_def['items']['type']
            i =0 
            while i < actual_number:
                temp = self.build_object(prop_key,obj_def['items'])
                if self.uniqueItems:
                    if temp not in result_array:
                        result_array.append(temp)
                        i+=1
                    else:
                        continue
                else:
                    result_array.append(temp)
                    i+=1
        return result_array

    def get_generator(self,obj_key, plugin_name, obj_def):
        if obj_key not in self.plugin_cache:
            generator=eval(plugin_name)(obj_def)
            self.plugin_cache[obj_key]=generator
        return self.plugin_cache[obj_key]


if __name__ == '__main__':
    allsamples=[f for f in sorted(os.listdir('../tests/samples')) if f.find('test_')!=-1]
    for sample in allsamples:
        schema=open('../tests/samples/'+sample, 'rb').read()
        producer=DataProducer(json.loads(schema))
        print '*'*10+sample+'*'*10
        print 'Schema:\n'+json.dumps(json.loads(schema),indent=4,sort_keys=True)
        print 'Generated Data:'
        for i in range(0,5):
            result = producer.produce()
            print json.dumps(result,indent=4, sort_keys=True)
