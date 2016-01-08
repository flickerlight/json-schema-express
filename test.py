import os
import json
from jsonschema import validate
from json_schema_express import DataProducer


allsamples=[f for f in sorted(os.listdir('json_schema_express/sample_schemas')) if f.find('test_')!=-1]
for sample in allsamples:
    schema=open('json_schema_express/sample_schemas/'+sample, 'rb').read()
    producer=DataProducer(json.loads(schema))
    print '*'*10+sample+'*'*10
    print 'Schema:\n'+json.dumps(json.loads(schema),indent=4,sort_keys=True)
    print 'Generated Data:'
    for i in range(0,5):
        result = producer.produce()
        print json.dumps(result,indent=4, sort_keys=True)
        try:
            validate(result,json.loads(schema))
        except:
            print "Not valid!"
