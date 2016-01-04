import random
class StdBooleanRandom:
    def __init__(self,config):
        random.seed()

    def generate(self):
        return random.choice([True,False])

if __name__ == '__main__':
    sbs=StdBooleanRandom({})
    for i in range(0,5):
        print sbs.generate()