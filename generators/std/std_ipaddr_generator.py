from faker import Factory

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

if __name__ == '__main__':
    ip4 = StdIPv4Random({})
    ip6 = StdIPv6Random({})
    for i in range(0,5):
        print ip4.generate()
        print ip6.generate()
