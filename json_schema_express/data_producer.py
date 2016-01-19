#!/usr/bin/env python

import json
import sys
import os
import random
from jsonschema import Draft4Validator
from jsonspec.pointer import extract

import codecs

import urllib2

from generators import *


class DataProducer:
    def __init__(self,schema,json_file_dir='.',generator_mapping=None):
        self.schema=schema
        self.generator_cache={}
        self.object_defines={}
        self.refered_jsons={}
        self.base_dir=json_file_dir
        self.base_uri=''
        self.type_vs_generator={
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
        if generator_mapping:
            for key,value in generator_mapping.items():
                self.type_vs_generator[key]=value

        self.__parse_schema()

    def __parse_schema(self):
        if '$schema' not in self.schema or self.schema['$schema'].find('draft-03')==-1:
            Draft4Validator.check_schema(self.schema)
        else:
            raise ValueError("Draft-03 schema is not supported currently.")

        self.object_defines['root']=self.schema
        if 'id' in self.schema:
            self.base_uri=self.schema['id']

        self.__parse_object('root',self.schema)


    def __get_refered_json(self,json_file=''):
        if not self.base_uri and not json_file:
            #refer to itself
            return self.schema
        elif json_file in self.refered_jsons:
            return self.refered_jsons[json_file]
        else:
            if self.base_uri:
                #refer to remote object
                opener=urllib2.build_opener()
                if json_file:
                    request=urllib2.Request(self.base_uri+'/'+json_file)
                else:
                    request=urllib2.Request(self.base_uri)
                request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36')
                resp=opener.open(request)
                json_content=json.loads(resp.read())
                opener.close()
            else:
                #refer to another local file
                f=codecs.open(self.base_dir+'/'+json_file,'r','utf-8')
                json_content=json.loads(f.read())
                f.close()
            self.refered_jsons[json_file]=json_content
            return json_content

    def __replace_ref(self,obj_key,ref_string):
        path=''
        for p in obj_key.split('.')[1:]:
            if not p.isdigit():
                path+=''.join(('[\'',p,'\']'))
            else:
                path+=''.join(('[',p,']'))
        (json_file,json_path)=ref_string.split('#')
        real_def = extract(self.__get_refered_json(json_file),json_path)
        exec('self.schema'+path+'='+json.dumps(real_def))

    def __parse_object(self,obj_key,obj_def):
        if obj_key == 'definitions':
            for df,value in obj_def.items():
                prop_key=obj_key+'.'+df
                self.___parse_object(prop_key,value)
        elif "$ref" in obj_def:
            #replace the whole object with referred json
            self.__replace_ref(obj_key,obj_def['$ref'])
        else:
            if obj_def['type'] == 'object':
                for key, value in obj_def['properties'].items():
                    self.__parse_object(obj_key+'.properties.'+key,value)
            elif obj_def['type'] == 'array':
                self.__parse_array(obj_key,obj_def)
            else:
                pass

    def __parse_array(self,obj_key,obj_def):
        if isinstance(obj_def['items'],list):
            for i in range(0,len(obj_def['items'])):
                prop_key = obj_key+'.items.'+str(i)
                self.__parse_object(prop_key,obj_def['items'][i])
        else:
            prop_key=obj_key
            self.__parse_object(prop_key,obj_def['items'])


    def __build_value(self,obj_key,obj_def):
        if '_generator_config' not in obj_def or 'generator' not in obj_def['_generator_config']:
            if 'format' in obj_def.keys():
                generator = self.__get_generator(obj_key, self.type_vs_generator[obj_def['format']],obj_def)
            else:
                generator = self.__get_generator(obj_key,self.type_vs_generator[obj_def['type']],obj_def)
        else:
            generator = self.__get_generator(obj_key,obj_def['_generator_config']['generator'],obj_def)
        return generator.generate()

    def __build_array(self,obj_key,obj_def):
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
                result_array.append(self.__build_object(prop_key, obj_def['items'][i]))
        else:
            actual_number = random.randrange(self.minLength,self.maxLength+1)
            prop_key = obj_key+'.'+obj_def['items']['type']
            i =0 
            while i < actual_number:
                temp = self.__build_object(prop_key,obj_def['items'])
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

    def __build_object(self,obj_key,obj_def):
        if obj_key in self.generator_cache:
            existing_generator = self.generator_cache[obj_key]
            return existing_generator.generate()
        else:
            if obj_def['type'] == 'object':
                result_object={}
                for key, definition in obj_def['properties'].items():
                    prop_key = obj_key+'.'+key
                    result_object[key] = self.__build_object(prop_key,definition)
                return result_object
            elif obj_def['type'] in ['string','integer','number','boolean']:
                return self.__build_value(obj_key,obj_def)
            elif obj_def['type'] == 'array':
                return self.__build_array(obj_key,obj_def)
            elif obj_def['type'] == 'null':
                return None
            else:
                raise ValueError('Unsupported value for object type: '+obj_def['type'])

    def produce(self):
        return self.__build_object('root',self.object_defines['root'])

    def __get_generator(self,obj_key, generator_name, obj_def):
        if obj_key not in self.generator_cache:
            generator=eval(generator_name)(obj_def)
            self.generator_cache[obj_key]=generator
        return self.generator_cache[obj_key]


if __name__ == '__main__':
    sample_dir='./sample_schemas'
    allsamples=[f for f in sorted(os.listdir(sample_dir)) if f.find('test_')!=-1]
    for sample in allsamples:
        schema=open(sample_dir+'/'+sample, 'rb').read()
        print '*'*10+sample+'*'*10
        producer=DataProducer(json.loads(schema),sample_dir)
        if sample.find('_ref_')!=-1:print '-> Original schema:\n'+ json.dumps(json.loads(schema),indent=4,sort_keys=True)
        print '-> Full schema:\n'+json.dumps(producer.schema,indent=4,sort_keys=True)
        print '-> Generated Data:'
        for i in range(0,1):
            result = producer.produce()
            print json.dumps(result,indent=4, sort_keys=True)
