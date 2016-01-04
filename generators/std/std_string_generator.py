import rstr
import string
import random

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
