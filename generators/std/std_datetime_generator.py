from datetime import datetime
import random


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

if __name__ == '__main__':
    sdr = StdDateTimeRandom({'_generator_config':{'from':'2014-12-31','to':'2015-10-03','date_format':'%Y-%m-%d'}})
    for i in range(0,5):
        print sdr.generate()
    sdr2 = StdDateTimeRandom({'_generator_config':{'from':'2014-12-31 10:00:00','to':'2015-10-03 10:00:00'}})
    for i in range(0,5):
        print sdr2.generate()