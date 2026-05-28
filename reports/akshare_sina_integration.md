# AkShare 新浪免费数据源验证记录

时间：2026-05-25

## 探测结果

可用：

- `akshare.stock_zh_a_daily`：新浪日线源，可访问；
- `akshare.stock_zh_a_hist_tx`：腾讯历史源，可访问，但字段较少；

不可用/有问题：

- `akshare.stock_zh_a_hist`：东方财富 `push2his.eastmoney.com`，当前环境连接失败。

## 已实现

新增：

```text
src/stock_assistant/akshare_provider.py
tests/test_akshare_provider.py
```

接入：

```bash
.venv/bin/python -m stock_assistant.case_check --case all --provider akshare-sina
.venv/bin/python -m stock_assistant.scanner --provider akshare-sina --codes 603912 --date 2022-12-29
.venv/bin/python backtests/tulong_backtest.py --provider akshare-sina --codes 603912 --start 2022-12-01 --end 2023-01-10
```

## 测试

```bash
.venv/bin/python -m pytest -q
```

结果：

```text
17 passed
```

## 真实案例检查

运行：

```bash
.venv/bin/python -m stock_assistant.case_check --case all --provider akshare-sina
```

结果：

```text
CaseResult(code='603912', name='佳力图', d2_date=datetime.date(2022, 12, 29), is_d1=True, is_d2=True, reason='D2冲高回落，量比1.41，未破支撑', signal_count=1)
CaseResult(code='603725', name='天安新材', d2_date=datetime.date(2023, 7, 28), is_d1=True, is_d2=False, reason='D2成交量/D1=5.28，超过2倍', signal_count=0)
```

## 结论

AkShare 新浪日线源能跑通当前两个正反案例：

- 佳力图：符合屠龙 D2，生成 D3 观察信号；
- 天安新材：D2/D1 量比 5.28，超过 2 倍，被排除。

这与用户提供的“屠龙战术”正反教材方向一致。
