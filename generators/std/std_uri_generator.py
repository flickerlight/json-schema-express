from faker import Factory

class StdURIRandom(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.uri()

if __name__ == '__main__':
    ser = StdURIRandom({})
    for i in range(0,5):
        print ser.generate()