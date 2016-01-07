from faker import Factory

class StdEmailRandom(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.email()

if __name__ == '__main__':
    ser = StdEmailRandom({})
    for i in range(0,5):
        print ser.generate()