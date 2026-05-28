# 东方财富 JSON 样本验证

用户在浏览器访问东方财富历史 K 线接口后，提供了 `603912` 佳力图 2022-12-15 ~ 2022-12-21 返回 JSON。已据此实现并测试：

- `src/stock_assistant/eastmoney.py`
  - `market_id_for_code()`
  - `bars_from_eastmoney_json()`
  - `EastmoneyDirectProvider`

测试文件：

- `tests/test_eastmoney.py`

验证命令：

```bash
.venv/bin/python -m pytest tests/test_eastmoney.py -q
```

结果：

```text
2 passed
```

全量测试：

```bash
.venv/bin/python -m pytest -q
```

结果：

```text
12 passed
```

## 解析结论

用户提供的 JSON 可以稳定解析为 `DailyBar`：

- `preKPrice` 用于第一根 K 线的 `prev_close`；
- 后续 K 线的 `prev_close` 使用上一交易日收盘价；
- `klines` 字段格式为：

```text
日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
```

## 真实请求状态

同样代码在本机 Python 直连时仍偶发/持续遇到：

```text
RemoteDisconnected('Remote end closed connection without response')
```

但浏览器可正常返回 JSON，说明：

- 东方财富账号密码不是必须条件；
- 更可能是东方财富对 Python/非浏览器请求、网络出口、TLS 指纹或频率有拦截；
- 后续可考虑改用 `curl_cffi` 模拟浏览器 TLS 指纹，或让用户导出/粘贴 JSON/CSV。
