import os,sys
import json
import unittest
from data_producer import DataProducer

class TestIntegerData(unittest.TestCase):
    def setUp(self):
        self.orginal_schema =self.schema = json.loads(open('./sample_schemas/test_integer.json','rb').read())

    def tearDown(self):
        self.schema=self.orginal_schema

    def test_random(self):
        dp=DataProducer(self.schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),range(self.schema['minimum'],self.schema['maximum']+1))

    def test_multipleof_positive(self):
        self.schema['multipleof']=5
        self.schema['minimum']=1
        self.schema['maximum']=20
        dp=DataProducer(self.schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),range(5,21,5))

    def test_multipleof_negative(self):
        self.schema['multipleof']=-5
        self.schema['minimum']=1
        self.schema['maximum']=20
        dp=DataProducer(self.schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),range(5,21,5))

    def test_exclusive_max(self):
        self.schema['exclusivemaximum']=True
        self.schema['minimum']=1
        self.schema['maximum']=2
        dp=DataProducer(self.schema)
        for i in range(0,5):
            self.assertEqual(dp.produce(),1)

    def test_exclusive_min(self):
        self.schema['exclusiveminimum']=True
        self.schema['minimum']=1
        self.schema['maximum']=2
        dp=DataProducer(self.schema)
        for i in range(0,5):
            self.assertEqual(dp.produce(),2)

    def test_no_border(self):
        self.schema.pop('minimum',None)
        self.schema.pop('maximum',None)
        dp=DataProducer(self.schema)
        for i in range(0,5):
            value=dp.produce()
            self.assertTrue(value>-sys.maxint-1)
            self.assertTrue(value<sys.maxint)

    def test_enum(self):
        self.schema['enum']=[34,15,52]
        dp=DataProducer(self.schema)
        for i in range(0,5):
            self.assertIn(dp.produce(),[34,15,52])

def Integer_Suite():
    ts =unittest.TestSuite()
    ts.addTest(unittest.makeSuite(TestIntegerData))
    return ts


if __name__=='__main__':
	mySuit = Integer_Suite()
	runner = unittest.TextTestRunner()
	runner.run(mySuit)


