from sysstra.orders.common import add_order_to_redis, fetch_orders_list
from sysstra.utils import send_order_alert
import datetime


def place_vt_order(app_db_cursor, rdb_cursor, order_candle, option_type, strike_price, position_type, quantity, transaction_type,
                   order_type, exit_type=None, quantity_left=0, params=None, market_type="options", trade_type=None,
                   trigger_price=None, lot_size=15, user_id=None, strategy_id=None, request_id=None, exchange="NSE"):
    """Function to Place Virtual Trading Order"""

    try:
        # logger.info(msg="* placing virtual trade order")
        order_dict = {"exchange": exchange,
                      "user_id": user_id,
                      "strategy_id": strategy_id,
                      "request_id": request_id,
                      "option_type": option_type,
                      "strike_price": strike_price,
                      "quantity": quantity,
                      "position_type": position_type,
                      "transaction_type": transaction_type,
                      "trade_type": trade_type,
                      "trade_action": trade_type,
                      "order_type": order_type,
                      "exit_type": exit_type,
                      "quantity_left": quantity_left,
                      "lot_size": lot_size
                      }

        if trigger_price:
            order_dict["trigger_price"] = trigger_price
        else:
            order_dict["trigger_price"] = order_candle["close"]
        order_dict["order_timestamp"] = datetime.datetime.now().replace(microsecond=0)
        order_dict["tradingsymbol"] = order_candle["symbol"]
        order_dict["date"] = order_candle["date"]
        if market_type == "cash":
            order_dict["expiry"] = ""
        else:
            order_dict["expiry"] = order_candle["expiry"]

        order_dict["day"] = order_candle["timestamp"].strftime("%A")
        if params:
            order_dict.update(params)

        # logger.info(msg="* vt_order : {}".format(order_dict))

        # Saving Order Details to Database
        save_vt_order(app_db_cursor=app_db_cursor, order_dict=order_dict.copy())

        # orders_list.append(order_dict)

        order_dict["user_id"] = str(order_dict["user_id"])
        order_dict["strategy_id"] = str(order_dict["strategy_id"])
        order_dict["request_id"] = str(order_dict["request_id"])
        order_dict["order_timestamp"] = str(order_dict["order_timestamp"])
        order_dict["date"] = str(order_dict["date"])
        order_dict["expiry"] = str(order_dict["expiry"])

        add_order_to_redis(rdb_cursor=rdb_cursor, request_id=str(request_id), order_dict=order_dict, mode="vt")
        orders_list = fetch_orders_list(rdb_cursor=rdb_cursor, request_id=str(request_id))

        # Creating Alert Dict
        alert_dict = {"user_id": str(order_dict["user_id"]),
                      "strategy_id": str(order_dict["strategy_id"]),
                      "request_id": str(order_dict["request_id"]),
                      "mode": "vt",
                      "exit_type": exit_type,
                      "symbol": order_candle["symbol"],
                      "quantity": quantity,
                      "price": order_dict["trigger_price"],
                      "quantity_left": quantity_left,
                      "trade_type": trade_type,
                      "template_id": 0
                      }

        # Sending Alert
        send_order_alert(alert_dict)

        return orders_list
    except Exception as e:
        print(f"Exception in placing virtual trade : {e}")
        pass


def save_vt_order(app_db_cursor, order_dict):
    """Function to save order in Database"""
    try:
        # logger.info(msg="* saving VT order to DB *****")

        app_db_cursor["vt_orders"].insert_one(order_dict)
    except Exception as e:
        print(f"Exception in saving VT order in DB : {e}")
        pass


def save_vt_trade(app_db_cursor, trade_dict):
    """Function to save order in Database"""
    try:
        # logger.info(msg="* saving VT trade to DB *****")
        app_db_cursor["vt_trades"].insert_one(trade_dict)
    except Exception as e:
        print(f"Exception in saving VT trade in DB : {e}")
        pass
