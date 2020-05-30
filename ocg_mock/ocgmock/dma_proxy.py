#!/usr/bin/env python3
"""
    HKEX Simulation
    Restful communication
"""

from flask import Flask, abort, request, jsonify
import uuid
import logging
app = Flask(__name__)
main_acct_dict = {10026135: 100017721, 10007761: 800003095}


def init_logger():
    log_format = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    # , format='%(asctime)s - %(name)% - %(levelname)s - %(message)s')
    logger_l = logging.getLogger(__name__)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler('logs/dma_proxy.log')
    f_handler.setLevel(logging.INFO)
    c_format = logging.Formatter(log_format)
    f_format = logging.Formatter(log_format)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    # logger_l.addHandler(c_handler)
    logger_l.addHandler(f_handler)
    return logger_l


@app.route('/otherfixuserlogin/login.do', methods=['POST'])
def login():
    login_token = str(uuid.uuid1())
    if not request.json or 'hsCode' not in request.json or 'passwordDigest' not in request.json:
        return jsonify({"errorList": {}, "errorMsg": "", "readFromCache": True, "success": True,
                        "successAndLogError": True, "warnList": []})
    user_id = int(request.json['hsCode'])
    logger.info('>>> login[user_id=%s]', user_id)
    if user_id in main_acct_dict:
        account_id = main_acct_dict[user_id]
    else:
        account_id = 100000000 + user_id
    return jsonify({"success": True, "readFromCache": True, "warnList": [],
                    "model": {"userStatus": True, "errorList": {}, "warnList": [],
                              "loginToken": login_token, "depositUsAssetAccountId": 0, "accountOwnerId": user_id,
                              "depositHkAssetAccountId": account_id, "errorMsg": "", "success": True,
                              "cashHkAssetAccountId": account_id, "successAndLogError": True, "cashUsAssetAccountId": 0}
                    })


@app.route('/otherfixaccount/queryAssetAccountDetail.do', methods=['POST'])
def query_account_info():
    if not request.json or 'hsCode' not in request.json or 'assetAccountId' not in request.json or 'market' not in request.json:
        abort(400)
    user_id = int(request.json['hsCode'])
    account_id = int(request.json['assetAccountId'])
    market = int(request.json['market'])
    logger.info('>>> queryAccountInfo[user_id=%s, account_id=%s, market=%s]', user_id, account_id, market)
    if market == 1:
        cash = 3000000
        trading_limit = 5000000
    else:
        cash = 0
        trading_limit = 0
    return jsonify({"success": True, "readFromCache": True, "warnList": [],
                    "model": {"assetAccountCode": "0", "assetAccountId": account_id, "cashCanUse": cash,
                              "tradingLimit": trading_limit, "accountOwnerCode": "0", "accountOwnerId": 0}})


@app.route('/otherfixaccount/queryStockHolding.do', methods=['POST'])
def query_positions():
    if not request.json or 'hsCode' not in request.json or 'assetAccountId' not in request.json or 'market' not in request.json:
        abort(400)
    user_id = int(request.json['hsCode'])
    account_id = int(request.json['assetAccountId'])
    market = int(request.json['market'])
    logger.info('>>> queryPositions[user_id=%s, account_id=%s, market=%s]', user_id, account_id, market)
    return jsonify({"success": True, "readFromCache": True,"warnList": [],
                    "model": [{"calAvailableShare": 1600, "stockCode": "5"},
                              {"calAvailableShare": 1000, "stockCode": "2"},
                              {"calAvailableShare": 4500, "stockCode": "1"}]})


@app.route('/otherfixtrade/uploadOtherFixTrade.do', methods=['POST'])
def upload_trade():
    user_id = int(request.json['hsCode'])
    account_id = int(request.json['assetAccountId'])
    market = int(request.json['market'])
    loginToken = request.json['loginToken']
    trade_list = request.json['otherFixTradeList']
    for trade in trade_list:
        money_type = int(trade['moneyType'])
        security_id = trade['stockCode']
        last_px = float(trade['price'])
        last_qty = int(trade['quantity'])
        price = float(trade['entrustPrice'])
        order_qty = int(trade['entrustQuantity'])
        order_id = trade['orderId']
        cl_ord_id = trade['orderIdFromParty']
        side = int(trade['entrustSide'])
        ord_status = int(trade['orderStatus'])
        cum_qty = int(trade['cumulativeQuantity'])
        leaves_qty = int(trade['leaveQuantity'])
        contra_broker_id = trade['contraBroker']
        transact_time = trade['transactTime']
        trade_match_id = trade['tradeMatchIdFromParty']
        sending_time = trade['sendingTime']
        logger.info('>>> upload_trade[user_id=%s, account_id=%s, market=%s, loginToken=%s, security_id=%s, price=%s, '
                    'order_qty=%s, side=%s, last_px=%s, last_qty=%s, ord_status=%s, cum_qty=%s, leaves_qty=%s, '
                    'order_id=%s, transact_time=%s, trade_match_id=%s]', user_id, account_id, market, loginToken,
                    security_id, price, order_qty, side, last_px, last_qty, ord_status, cum_qty, leaves_qty, order_id,
                    transact_time, trade_match_id)
        return jsonify({"errorList": {}, "errorMsg": "",
                        "model": "Total upload 1 record(s), Success: 1 record(s), Failure: 0 record(s)",
                        "readFromCache": True, "success": True, "successAndLogError": True, "warnList": []})


if __name__ == "__main__":
    logger = init_logger()
    app.run(host="0.0.0.0", port=18214)
    # , debug=True)
