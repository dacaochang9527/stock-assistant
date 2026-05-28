# A 股中短线选股助手

> 目标：构建一个面向个人使用的 A 股中短线波段 +「屠龙战术」选股、监控、提醒与复盘工具。

## 边界声明

本项目只输出策略信号、候选池、风险位、失效条件和复盘数据，不构成投资建议，不保证收益，也不自动交易。最终买卖决策由使用者自行承担。

## 已实现范围

- Phase 1：离线扫描版
  - CSV 数据源；
  - akshare 可选适配器；
  - MA、EXPMA、涨停、滚动高点等基础指标；
  - 屠龙战术 D1/D2 识别；
  - 波段突破候选识别；
  - Markdown 日报生成。
- Phase 2：屠龙回测版
  - D1/D2/D3/D4/D5 状态回放；
  - 胜率、平均收益、最好/最差收益摘要；
  - 最近交易明细输出。
- Phase 3：盘中提醒版
  - 读取观察池和当前价 CSV；
  - D3 水下观察提醒；
  - 跌破失效价提醒；
  - 30 分钟去重；
  - 文件通知器。
- Phase 4：个人复盘版
  - CSV 复盘日志；
  - 周报生成。

## 项目结构

```text
a-share-stock-assistant/
├── config/                 # 策略、股票池、提醒配置
├── data/                   # 本地行情与候选池数据
├── reports/                # 每日报告与提醒日志
├── src/stock_assistant/    # 核心源码
├── backtests/              # 回测脚本
└── tests/                  # 测试
```

## 快速验证

已创建 Python 3.11 虚拟环境并安装依赖：

```bash
cd /Users/fenomenoronaldo/Documents/ai-project/a-share-stock-assistant
source .venv/bin/activate
python -m pytest -q
```

当前验证结果：

```text
10 passed
```

如果不想激活 venv，也可以直接：

```bash
.venv/bin/python -m pytest -q
```

## 收盘扫描

```bash
PYTHONPATH=src python -m stock_assistant.scanner \
  --provider csv \
  --date 2024-01-03 \
  --data-dir data/raw \
  --output reports/daily/sample.md
```

接入 akshare 后：

```bash
PYTHONPATH=src python -m stock_assistant.scanner --provider akshare --date 2026-01-01 --limit 100
```

## 屠龙回测

```bash
PYTHONPATH=src python backtests/tulong_backtest.py \
  --provider csv \
  --data-dir data/raw \
  --start 2024-01-01 \
  --end 2024-01-06
```

## 盘中提醒模拟

准备：

```text
data/watchlists/tulong_d3.csv
code,name,trigger_price,invalid_price
000001,样例,10.9,10.0

data/watchlists/current_prices.csv
code,price
000001,10.7
```

运行：

```bash
PYTHONPATH=src python -m stock_assistant.intraday_monitor \
  --watchlist data/watchlists/tulong_d3.csv \
  --prices data/watchlists/current_prices.csv \
  --out reports/alerts.log
```

## 周报

```bash
PYTHONPATH=src python -m stock_assistant.weekly_review \
  --journal data/journal.csv \
  --week-end 2024-01-07
```

### Tushare 数据源

Tushare token 放在本地 `.env`：

```text
TUSHARE_TOKEN=...
```

`.env` 已加入 `.gitignore`，不要提交。

运行案例检查：

```bash
.venv/bin/python -m stock_assistant.case_check --case all --provider tushare
```

当前验证记录见：

```text
reports/tushare_integration.md
```

注意：当前 token 可读取，但账号暂未开通 `stock_basic` 和 `daily` 接口权限。

### 免费数据源：AkShare 新浪日线

东方财富直连、curl_cffi、Playwright 在当前环境下都可能被断开；Tushare token 当前没有 `daily` 权限。已改用 AkShare 的新浪日线源：

```bash
.venv/bin/python -m stock_assistant.case_check --case all --provider akshare-sina
```

当前真实案例验证通过：

```text
佳力图 603912：符合屠龙 D2，生成 D3 观察信号
天安新材 603725：D2/D1 量比 5.28，超过 2 倍，被排除
```

记录见：

```text
reports/akshare_sina_integration.md
```

## 后续建议

1. 已根据浏览器返回 JSON 新增东方财富直连解析器，验证记录见：

```text
reports/eastmoney_json_sample.md
```

2. 东方财富账号密码不是必须条件；历史 K 线公开 JSON 中已经包含策略所需字段。当前 Python 直连、curl_cffi、系统 curl、Playwright 自动化浏览器仍可能被远端断开；记录见：

```text
reports/curl_cffi_eastmoney.md
reports/playwright_eastmoney.md
```

3. 换网络或备用数据源后，重新运行真实案例检查：

```bash
NO_PROXY='*' no_proxy='*' .venv/bin/python -m stock_assistant.case_check --case all --provider eastmoney
```

4. 增加市场情绪过滤器：涨停家数、跌停家数、连板高度；
5. 增强涨停价规则：ST、创业板、科创板、北交所差异；
6. 如有 tushare token，可增加 tushare provider 作为备用真实数据源。
