import requests
import datetime
import json
from sysstra.orders.common import add_order_to_redis, fetch_orders_list
from sysstra.utils import send_order_alert
from sysstra.config import config
orders_url = config.get("orders_url")


def place_lt_order(tradingsymbol, quantity, transaction_type, order_type, lot_size=15, exchange="NSE",
                   credential_id=None, trigger_price=None, order_price=None):
    """ Function to Place Live Trading Order """
    try:

        if order_type == "MARKET":
            order_data_params = {"tradingsymbol": tradingsymbol,
                                 "exchange": exchange,
                                 "transaction_type": transaction_type,
                                 "quantity": quantity * lot_size,
                                 "order_type": order_type,
                                 "product": "MIS",
                                 "validity": "DAY"}

            order_response = place_live_order(credential_id=credential_id, order_details=order_data_params)

            if order_response["status"] == "COMPLETE":
                # return "success", order_response["broker_response"][0]["broker_response"]
                return "success", order_response
            else:
                return "failed", None

        elif order_type == "SL":
            order_data_params = {"tradingsymbol": tradingsymbol, "exchange": exchange,
                                 "transaction_type": transaction_type,
                                 "quantity": quantity * lot_size, "product": "MIS", "validity": "DAY",
                                 "order_type": "SL", "trigger_price": trigger_price, "price": order_price}
            order_response = place_live_order(credential_id=credential_id, order_details=order_data_params)

            if order_response["status"] == "success":
                # return "success", order_response["data"]["order_id"]
                # return "success", order_response["order_id"][0]
                return "success", order_response["order_id"]
            else:
                return "failed", None

        elif order_type == "LIMIT":
            order_data_params = {"tradingsymbol": tradingsymbol, "exchange": exchange,
                                 "transaction_type": transaction_type, "quantity": quantity * lot_size,
                                 "product": "MIS", "validity": "TTL", "validity_ttl": 1,
                                 "order_type": "LIMIT",  "price": order_price}

            order_response = place_live_order(credential_id=credential_id, order_details=order_data_params)

            if order_response["status"] == "success":
                # return "success", order_response["data"]["order_id"]
                # return "success", order_response["order_id"][0]
                return "success", order_response["order_id"]
            else:
                return "failed", None

    except Exception as e:
        print(f"Exception in placing live trade : {e}")
        return "failed", None


def save_lt_order(app_db_cursor, rdb_cursor, tradingsymbol, option_type, strike_price, position_type, quantity, transaction_type, order_type,
                  orders_list, exit_type=None, quantity_left=0, params=None, market_type="cash", trade_type=None,
                  expiry=None, trigger_price=None, lot_size=25, user_id=None, strategy_id=None, request_id=None,
                  exchange="NSE", exchange_timestamp=None, order_id=None, broker_response=None, sl_order_id=None):

    """Function to save order in Database"""
    try:
        order_dict = {"exchange": exchange, "user_id": user_id, "strategy_id": strategy_id,
                      "request_id": request_id, "tradingsymbol": tradingsymbol, "transaction_type": transaction_type,
                      "quantity": quantity, "position_type": position_type, "order_type": order_type,
                      "exit_type": exit_type, "quantity_left": quantity_left, "lot_size": lot_size, "trade_type": trade_type,
                      "trade_action": trade_type,
                      "exchange_timestamp": exchange_timestamp, "status": "COMPLETE", "trigger_price": trigger_price, "order_id": order_id}

        if sl_order_id:
            order_dict["sl_order_id"] = sl_order_id

        if market_type == "cash":
            order_dict["expiry"] = ""
            order_dict["option_type"] = ""
            order_dict["strike_price"] = ""
        else:
            order_dict["expiry"] = expiry
            order_dict["option_type"] = option_type
            order_dict["strike_price"] = strike_price

        order_dict["order_timestamp"] = exchange_timestamp
        order_dict["date"] = datetime.datetime.strptime(str(datetime.datetime.today().date()), '%Y-%m-%d')
        order_dict["day"] = order_dict["date"].strftime("%A")

        if params:
            order_dict.update(params)

        # Creating New Dict for saving data in to db
        lt_order_dict = {}
        for key in order_dict.keys():
            lt_order_dict[key] = order_dict[key]

        lt_order_dict["order_id"] = order_id
        lt_order_dict["broker_response"] = broker_response
        lt_order_dict["trade_action"] = lt_order_dict["trade_type"]

        # Saving Order Details to Database
        app_db_cursor["lt_orders"].insert_one(lt_order_dict)

        order_dict["strategy_id"] = str(order_dict["strategy_id"])
        order_dict["request_id"] = str(order_dict["request_id"])
        order_dict["user_id"] = str(order_dict["user_id"])
        order_dict["order_timestamp"] = str(order_dict["order_timestamp"])
        order_dict["exchange_timestamp"] = str(order_dict["exchange_timestamp"])
        order_dict["expiry"] = str(order_dict["expiry"])
        order_dict["date"] = str(order_dict["date"])
        order_dict["order_id"] = order_id

        add_order_to_redis(rdb_cursor=rdb_cursor, request_id=str(request_id), order_dict=order_dict, mode="lt")
        orders_list = fetch_orders_list(rdb_cursor=rdb_cursor, request_id=str(request_id))

        # Creating Alert Dict
        alert_dict = {"user_id": str(order_dict["user_id"]),
                      "strategy_id": str(order_dict["strategy_id"]),
                      "request_id": str(order_dict["request_id"]),
                      "mode": "lt",
                      "exit_type": exit_type,
                      "symbol": tradingsymbol,
                      "quantity": quantity,
                      "price": trigger_price,
                      "quantity_left": quantity_left,
                      "trade_type": trade_type,
                      "template_id": 0
                      }

        # Sending Alert
        send_order_alert(alert_dict)
        return "success", orders_list

    except Exception as e:
        print(f"Exception in Saving Order in DB : {e}")
        return "failed", orders_list


def save_lt_trade(app_db_cursor, trade_dict):
    """Function to save order in Database"""
    try:
        # logger.info(msg="* saving LT trade to DB *****")
        app_db_cursor["lt_trades"].insert_one(trade_dict)
    except Exception as e:
        print(f"Exception in saving LT trade in DB : {e}")
        pass


def place_live_order(credential_id, order_details):
    """Function to place live trade order via REST API"""
    try:
        print("Placing Live Trade Order")
        request_dict = {"credential_id": str(credential_id),
                        "order_details": json.dumps(order_details)}
        print("request_dict : {}".format(request_dict))

        response = requests.post(url=orders_url+"place_order", params=request_dict)
        print("******** Order Placement Response *********")
        print(response.json())
        return response.json()
    except Exception as e:
        print("Exception in placing live trade order : {}".format(e))
        return None


def modify_live_order(credential_id, order_details):
    """Function to Modify Live Order"""
    try:
        print("* Modifying Live Order")
        request_dict = {"credential_id": str(credential_id),
                        "order_details": json.dumps(order_details)}
        print("request_dict : {}".format(request_dict))

        response = requests.post(url=orders_url + "modify_order", params=request_dict)
        print("******** Order Placement Response *********")
        print(response.json())
        return response.json()
    except Exception as e:
        print("Exception in Modify Live Order : {}".format(e))
        pass
