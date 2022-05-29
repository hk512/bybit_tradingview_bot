import configparser

conf = configparser.ConfigParser()
conf.read('config.ini')

api_key = conf['bybit']['api_key']
api_secret = conf['bybit']['api_secret']

symbol = conf['trade']['symbol']
leverage = int(conf['trade']['leverage'])
lot = float(conf['trade']['lot'])
max_lot = float(conf['trade']['max_lot'])

line_token = conf['line']['line_token']
