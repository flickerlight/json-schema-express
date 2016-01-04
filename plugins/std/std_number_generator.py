import random
import sys

class StdNumberRandom(object):

    def __init__(self,config):

        if not self._validate_config(config):
            raise ValueError('Not a valid json schema for Number(float) type')

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

    def _validate_config(self,config):
        if 'multipleof' in config.keys() and type(config['multipleof']) not in [int,float]: return False
        if 'minimum' in config.keys() and type(config['minimum']) not in [int,float]:return False
        if 'maximum' in config.keys() and type(config['maximum']) not in [int,float]:return False
        if 'exclusiveminimum' in config.keys() and not isinstance(config['exclusiveminimum'],bool):return False
        if 'exclusivemaximum' in config.keys() and not isinstance(config['exclusivemaximum'],bool):return False
        if 'minimum' in config.keys() and 'maximum' in config.keys() and config['maximum']<config['minimum']: return False
        return True

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

if __name__ == '__main__':
    print 'Generate 5 random floats in [1.0,10.0]'
    snr = StdNumberRandom({'maximum':10.0,'minimum':1.0})
    for i in range(0,5):
        print snr.generate()
