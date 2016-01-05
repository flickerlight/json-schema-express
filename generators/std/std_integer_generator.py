import random
import sys
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
        if 'minimum' in config.keys():
            self.min = int(config['minimum'])
        if 'maximum' in config.keys():
            self.max = int(config['maximum'])

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
            output =  random.randrange(self.realmin,self.max,self.multipleof)
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
        

