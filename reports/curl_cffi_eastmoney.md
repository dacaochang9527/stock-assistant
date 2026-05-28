# curl_cffi 东方财富直连验证记录

时间：2026-05-25

## 已实现

`src/stock_assistant/eastmoney.py` 中的 `EastmoneyDirectProvider` 已支持：

- 默认使用 `curl_cffi.requests.get(..., impersonate="chrome120")`；
- 设置浏览器 UA、Referer、Accept；
- `session.trust_env = False` 的 requests fallback；
- 独立函数：
  - `eastmoney_kline_params()`
  - `eastmoney_headers()`
  - `bars_from_eastmoney_json()`

## 测试

```bash
.venv/bin/python -m pytest -q
```

结果：

```text
13 passed
```

## 真实请求结果

运行：

```bash
NO_PROXY='*' no_proxy='*' .venv/bin/python -m stock_assistant.case_check --case all --provider eastmoney
```

结果：

```text
603912 佳力图 2022-12-29: 数据获取失败：ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
603725 天安新材 2023-07-28: 数据获取失败：ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

单独验证 curl_cffi：

```text
curl_cffi.requests.exceptions.ConnectionError: Failed to perform, curl: (56) Connection closed abruptly.
```

系统 curl 验证：

```text
curl: (52) Empty reply from server
```

## 结论

- 浏览器可以访问，说明接口和参数没有问题；
- Python requests、curl_cffi、系统 curl 都会被服务端关闭连接；
- 这不是东方财富账号登录问题；
- 更可能是本机网络出口、系统代理/透明代理、东方财富对非浏览器请求的额外检测，或浏览器携带了某些环境上下文。

## 下一步可选方案

1. 用浏览器开发者工具复制请求为 cURL，保留完整请求头，但删除 Cookie 后尝试；
2. 增加“本地 JSON 导入”命令，直接解析浏览器保存的 JSON；
3. 改用 Tushare 数据源；
4. 使用 Playwright 驱动浏览器获取 JSON，再交给本项目解析。
