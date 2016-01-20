import random
import sys
import string
import rstr
from datetime import datetime
from faker import Factory


class StdBooleanRandom:
    def __init__(self,config):
        random.seed()

    def generate(self):
        return random.choice([True,False])

class StdIntegerRandom(object):
    '''Generate a random integer in given range. Support standard json keys "maximum","minimum","multipleof" and "enum" for integer.'''
    def __init__(self,config):

        self.realmin = self.min = -sys.maxint-1
        self.max = sys.maxint
        self.multipleof = 1
        self.exclusivemin = False
        self.exclusivemax = False
        self.enum = []

        random.seed()

        if 'enum' in config.keys():
            self.enum = config['enum']

        if 'multipleof' in config.keys():
            self.multipleof = config['multipleof']
        if self.multipleof<0: self.multipleof=-self.multipleof
        if 'minimum' in config.keys():
            self.min = int(config['minimum'])
        if 'maximum' in config.keys():
            self.max = int(config['maximum'])

        if not isinstance(self.min,int) or not isinstance(self.max,int) or not isinstance(self.multipleof,int):
            raise ValueError("Wrong parameter (min/max/multipleof) type for Integer generator")

        if 'exclusivemaximum' in config.keys() and config['exclusivemaximum'] == True:
            self.exclusivemax = True
        if 'exclusiveminimum' in config.keys() and config['exclusiveminimum'] == True:
            self.exclusivemin = True

        self.realmin = self.min
        while self.realmin % self.multipleof:
            self.realmin += 1

        if self.realmin > self.max:
            raise ValueError('Wrong range for Integer type')

    def generate(self):
        if self.enum:
            return random.choice(self.enum)
        while True:
            output =  random.randrange(self.realmin,self.max+1,self.multipleof)
            if self.exclusivemax and output == self.max:
                continue
            if self.exclusivemin and output == self.min:
                continue
            return output

class StdIntegerSequence:
    '''Define an integer sequence with specified start and step parameters, and return one element each time generate() is called'''
    def __init__(self,config):
        self.start = config['_generator_config']['start']
        self.step = config['_generator_config']['step']
        self.current = self.start-self.step

    def generate(self):
        self.current +=self.step
        return self.current

class StdNumberRandom(object):
    '''Generate a random float in given range. Support standard json keys "maximum","minimum","multipleof" and "enum" for float number.'''

    def __init__(self,config):
        self.min = 0.0
        self.max = 1000.0
        self.multipleof = 1.0
        self.exclusivemin = self.exclusivemax = False
        self.start = self.end = None
        self.enum = []

        random.seed()

        if 'multipleof' in config.keys():
            self.multipleof = config['multipleof']
        if 'minimum' in config.keys():
            self.min = float(config['minimum'])
        if 'maximum' in config.keys():
            self.max = float(config['maximum'])

        if 'exclusivemaximum' in config.keys() and config['exclusivemaximum'] == True:
            self.exclusivemax = True
        if 'exclusiveminimum' in config.keys() and config['exclusiveminimum'] == True:
            self.exclusivemin = True

        if self.multipleof != 1.0:
            if (self.min/self.multipleof).is_integer():
                self.start = int(self.min/self.multipleof)
            else:
                self.start = int(self.min/self.multipleof)+1
            self.end = int(self.max/self.multipleof)
            if self.start > self.end:
                raise ValueError('Wrong range for Number(float) type.')
        else:
            if self.min>self.max:
                raise ValueError('Wrong range for Number(float) type.')

        if 'enum' in config.keys():
            self.enum = enum

    def generate(self):
        if self.enum:
            return random.choice(self.enum)
        else:
            while True:
                if self.multipleof == 1.0:
                    output = random.uniform(self.min,self.max)
                else:
                    output =  self.multipleof*random.randrange(self.start,self.end)
                if self.exclusivemax and output == self.max:
                    continue
                if self.exclusivemin and output == self.min:
                    continue
                return output

class StdStringRandom(object):
    def __init__(self,config,minLength=1,maxLength=10):
        self.minLength = minLength
        self.maxLength = maxLength
        self.pattern = None
        self.enum = []

        random.seed()

        if 'minLength' in config.keys():
            if not isinstance(self.minLength,int):
                raise ValueError('Not valid minLength for string')
            self.minLength = config['minLength']
        if 'maxLength' in config.keys():
            if not isinstance(self.maxLength,int):
                raise ValueError('Not valid maxLength for string')
            if self.maxLength<self.minLength:
                raise ValueError('MaxLength should be bigger than minLength for string.')
            self.maxLength = config['maxLength']

        if 'pattern' in config.keys():
            self.pattern = config['pattern']

        if 'enum' in config.keys():
            self.enum = config['enum']

    def generate(self):
        if self.enum:
            return random.choice(self.enum)
        elif self.pattern:
            return rstr.xeger(self.pattern)
        else:
            return rstr.rstr(string.letters+string.digits,self.minLength,self.maxLength)

class StdDateTimeRandom:
    def __init__(self,config):

        if 'date_format' in config['_generator_config']:
            self.date_format = config['_generator_config']['date_format']
        else:
            self.date_format = '%Y-%m-%d %H:%M:%S'
        if 'from' in config['_generator_config']:
            self.from_long = int((datetime.strptime(config['_generator_config']['from'],self.date_format)-datetime(1970,1,1)).total_seconds())
        else:
            self.from_long = 0
        if 'to' in config['_generator_config']:
            self.to_long = int((datetime.strptime(config['_generator_config']['to'],self.date_format)-datetime(1970,1,1)).total_seconds())
        else:
            self.to_long = int((datetime(2500,1,1)-datetime(1970,1,1)).total_seconds())
        random.seed()

    def generate(self):
        seconds = random.randint(self.from_long,self.to_long)
        return datetime.fromtimestamp(seconds).strftime(self.date_format)

class StdDomainNameRandom(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.domain_name()

class StdEmailRandom(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.email()

class StdIPv4Random(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.ipv4()

class StdIPv6Random(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.ipv6()

class StdURIRandom(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.uri()