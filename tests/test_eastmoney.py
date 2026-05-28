from stock_assistant.eastmoney import bars_from_eastmoney_json, eastmoney_kline_params, market_id_for_code


SAMPLE = {
    "rc": 0,
    "data": {
        "code": "603912",
        "market": 1,
        "name": "佳力图",
        "preKPrice": 9.98,
        "klines": [
            "2022-12-15,9.93,10.17,10.20,9.93,38877,39386980.00,2.71,1.90,0.19,1.28",
            "2022-12-16,10.18,10.28,10.35,9.95,61371,62330324.00,3.93,1.08,0.11,2.02",
            "2022-12-19,10.38,11.31,11.31,10.24,184039,202423504.00,10.41,10.02,1.03,6.06",
            "2022-12-20,12.44,12.44,12.44,12.01,289093,359055463.00,3.80,9.99,1.13,9.52",
            "2022-12-21,11.20,12.02,12.44,11.20,384033,454377104.00,9.97,-3.38,-0.42,12.64",
        ],
    },
}


def test_market_id_for_code():
    assert market_id_for_code("603912") == 1
    assert market_id_for_code("000001") == 0
    assert market_id_for_code("300750") == 0


def test_eastmoney_kline_params_uses_secid_and_date_range():
    params = eastmoney_kline_params("603912")
    assert params["secid"] == "1.603912"
    assert params["klt"] == "101"
    assert params["fqt"] == "0"


def test_bars_from_eastmoney_json_parses_prev_close_and_limit_up():
    bars = bars_from_eastmoney_json(SAMPLE)
    assert len(bars) == 5
    assert bars[0].prev_close == 9.98
    assert bars[0].limit_up_price == 10.98
    assert bars[2].close == 11.31
    assert bars[2].limit_up_price == 11.31
    assert bars[-1].name == "佳力图"
