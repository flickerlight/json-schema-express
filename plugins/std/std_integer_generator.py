import random
import sys
class StdIntegerRandom(object):
    '''Generate a random integer in given range. Support standard json keys "maximum","minimum","multipleof" and "enum" for integer.'''
    def __init__(self,config):

        if not self._validate_config(config):
            raise ValueError('Not a valid json schema for Integer type')

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


    def _validate_config(self,config):
        if 'multipleof' in config.keys() and not isinstance(config['multipleof'],int): return False
        if 'minimum' in config.keys() and not isinstance(config['minimum'],int):return False
        if 'maximum' in config.keys() and not isinstance(config['maximum'],int):return False
        if 'exclusiveminimum' in config.keys() and not isinstance(config['exclusiveminimum'],bool):return False
        if 'exclusivemaximum' in config.keys() and not isinstance(config['exclusivemaximum'],bool):return False
        if 'minimum' in config.keys() and 'maximum' in config.keys() and config['maximum']<config['minimum']: return False
        return True

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
        self.start = config['start']
        self.step = config['step']
        self.current = self.start

    def generate(self):
        self.current +=self.step
        return self.current
        

