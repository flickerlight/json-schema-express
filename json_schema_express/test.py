import os,sys
import json
from copy import deepcopy
import unittest
from data_producer import DataProducer

class TestInteger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f=open('./sample_schemas/test_integer.json','rb')
        cls.original_schema=json.loads(f.read())
        f.close()

    def test_random(self):
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


def Integer_Suite():
    ts =unittest.TestSuite()
    ts.addTest(unittest.makeSuite(TestInteger))
    return ts


class TestFloatData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f = open('./sample_schemas/test_float.json','rb')
        cls.orginal_schema = json.loads(f.read())
        f.close()


def Float_Suite():
    ts = unittest.TestSuite()

if __name__=='__main__':
	mySuit = Integer_Suite()
	runner = unittest.TextTestRunner()
	runner.run(mySuit)


