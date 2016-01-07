from faker import Factory

class StdDomainNameRandom(object):
    def __init__(self,config):
        self.factory = Factory.create()

    def generate(self):
        return self.factory.domain_name()

if __name__ == '__main__':
    sdnr = StdDomainNameRandom({})
    for i in range(0,5):
        print sdnr.generate()