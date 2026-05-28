# Playwright 东方财富抓取验证记录

时间：2026-05-25

## 已完成

已安装 Playwright：

```bash
.venv/bin/python -m pip install playwright
```

本机已有系统浏览器：

- Google Chrome
- Microsoft Edge

已实现：

```text
src/stock_assistant/eastmoney_playwright.py
```

并接入：

```text
stock_assistant.case_check --provider eastmoney-playwright
stock_assistant.scanner --provider eastmoney-playwright
```

## 验证结果

测试通过：

```bash
.venv/bin/python -m pytest -q
```

```text
13 passed
```

真实请求：

```bash
.venv/bin/python -m stock_assistant.case_check --case jialitu --provider eastmoney-playwright
```

结果：

```text
Page.goto: net::ERR_EMPTY_RESPONSE
```

与 requests / curl_cffi / 系统 curl 的表现一致，说明 Playwright 启动的自动化浏览器也被当前网络/服务端断开。

## 已支持的额外选项

`EastmoneyPlaywrightProvider` 支持 `EASTMONEY_CHROME_USER_DATA_DIR` 环境变量，可使用持久化 Chrome Profile：

```bash
EASTMONEY_CHROME_USER_DATA_DIR=.chrome-eastmoney-profile \
.venv/bin/python -m stock_assistant.case_check --case all --provider eastmoney-playwright
```

但当前测试仍返回 `ERR_EMPTY_RESPONSE`。

## 重要观察

通过 macOS `open -a 'Google Chrome' URL` 打开的普通 Chrome 浏览器仍可由用户手动访问该 URL；而自动化浏览器、requests、curl_cffi、curl 均失败。

这意味着后续最可能可行的是：

1. 使用用户正常 Chrome Profile 的 DevTools Protocol 连接已有浏览器；
2. 或者让用户用普通 Chrome 保存 JSON 文件，再走本地 JSON 导入；
3. 或者改接 Tushare。
