from argparse import ArgumentParser
import logging
import sys

from flask import Flask
from flask import jsonify
from flask import request
import pybybit
import requests

import config

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='[%(levelname)s][%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)


@app.route('/', methods=['POST'])
def run():
    side = request.data.decode()

    if side != 'Buy' and side != 'Sell':
        notificator = Notificator(token=config.line_token)
        notificator.notify(message=f'signal({side}) is incorrect.')
        return jsonify({
            'result': -1
        }), 400

    trader = Trader(
        key=config.api_key, secret=config.api_secret, symbol=config.symbol, lot=config.lot, side=side,
        leverage=config.leverage
    )

    close_position_result = trader.close_position()

    if not close_position_result:
        notificator = Notificator(token=config.line_token)
        notificator.notify(message='failed close position.')
        return jsonify({
            'result': -1
        }), 400

    create_position_result = trader.create_position()

    if not create_position_result:
        notificator = Notificator(token=config.line_token)
        notificator.notify(message='failed create position.')
        return jsonify({
            'result': -1
        }), 400

    return jsonify({
        'result': 0
    }), 200


class Trader(object):
    def __init__(self, key, secret, symbol, lot, side, leverage):
        self.symbol = symbol
        self.client = pybybit.API(key=key, secret=secret, testnet=False)

        # 1オーダ当たりの発注量、単位はBTC
        self.lot = lot

        self.side = side

        # # クロスマージンモードに設定
        # self.client.rest.linear.private_position_switchisolated(symbol=symbol, is_isolated=False,
        #                                                         buy_leverage=leverage, sell_leverage=leverage)
        # レバレッジを設定
        self.client.rest.linear.private_position_setleverage(symbol=symbol, buy_leverage=leverage,
                                                             sell_leverage=leverage)

    def get_position_size(self, side):
        response = self.client.rest.linear.private_position_list(symbol=self.symbol)

        if response.status_code != 200:
            logger.error({
                'action': 'get_position',
                'status_code': response.status_code
            })
            return None

        response_data = response.json()

        if response_data['ret_code'] != 0:
            logger.error({
                'action': 'get_position',
                'ret_code': response_data['ret_code'],
                'ret_msg': response_data['ret_msg']
            })
            return None

        logger.info({
            'action': 'get_position',
            'result': response_data['result'],
        })

        result = response_data['result']
        if side == 'Buy':
            return result[0]['size']
        elif side == 'Sell':
            return result[1]['size']

    def order(self, side, size, reduce_only):

        response = self.client.rest.linear.private_order_create(
            side=side, symbol=self.symbol, order_type="Market", qty=size, reduce_only=reduce_only,
            time_in_force='GoodTillCancel', close_on_trigger=False)

        if response.status_code != 200:
            logger.error({
                'action': 'order',
                'status_code': response.status_code
            })
            return False

        response_data = response.json()

        if response_data['ret_code'] != 0:
            logger.error({
                'action': 'order',
                'ret_code': response_data['ret_code'],
                'ret_msg': response_data['ret_msg']
            })
            return False

        logger.info({
            'action': 'order',
            'result': response_data['result'],
        })

        return True

    def create_position(self, max_iteration=10):
        for _ in range(max_iteration):
            result = self.order(side=self.side, size=self.lot, reduce_only=False)
            if result:
                return True

        return False

    def close_position(self, max_iteration=10):
        for _ in range(max_iteration):
            if self.side == 'Buy':
                size = self.get_position_size(side='Sell')
            elif self.side == 'Sell':
                size = self.get_position_size(side='Buy')

            if size is None:
                continue

            if size == 0:
                return True

            result = self.order(side=self.side, size=size, reduce_only=True)

            if result:
                return True

        return False


class Notificator(object):
    def __init__(self, token):
        self.token = token

    def notify(self, message):
        try:
            headers = {"Authorization": "Bearer " + self.token}
            payload = {"message": message}
            requests.post('https://notify-api.line.me/api/notify', headers=headers, params=payload)
        except Exception as e:
            logger.info({
                'action': 'notify',
                'error': e.args
            })


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=80, type=int, help='port to listen on')
    parser.add_argument('-i', '--ip', default='0.0.0.0', type=str, help='ip to listen on')
    args = parser.parse_args()
    port = args.port
    ip = args.ip

    app.run(host=ip, port=port, threaded=True, debug=True)
