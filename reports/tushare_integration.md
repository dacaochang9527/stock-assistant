# Tushare 接入验证记录

时间：2026-05-25

## 已完成

- 已将 `TUSHARE_TOKEN` 写入项目本地 `.env`。
- `.env` 已加入 `.gitignore`，避免误提交。
- 已安装依赖：
  - `tushare`
  - `python-dotenv`
- 已实现：
  - `src/stock_assistant/tushare_provider.py`
  - `tests/test_tushare_provider.py`
- 已接入：
  - `stock_assistant.case_check --provider tushare`
  - `stock_assistant.scanner --provider tushare`

## 测试

```bash
.venv/bin/python -m pytest -q
```

结果：

```text
15 passed
```

## 真实接口验证

运行：

```bash
.venv/bin/python -m stock_assistant.case_check --case all --provider tushare
```

结果：

```text
603912 佳力图 2022-12-29: 数据获取失败：Exception: 抱歉，您没有接口(daily)访问权限，权限的具体详情访问：https://tushare.pro/document/1?doc_id=108。
603725 天安新材 2023-07-28: 数据获取失败：Exception: 抱歉，您没有接口(daily)访问权限，权限的具体详情访问：https://tushare.pro/document/1?doc_id=108。
```

进一步测试：

- `stock_basic`：无权限；
- `daily`：无权限。

## 结论

Token 可被项目读取，但该 Tushare 账号当前没有 `stock_basic` 和 `daily` 接口权限，无法获取 A 股基础列表和日线行情。

## 后续选择

1. 在 Tushare 获取/升级到包含 `stock_basic` 和 `daily` 的权限；
2. 改用 Tushare 可访问的其他接口，如果账号有权限；
3. 继续使用本地 CSV / 浏览器 JSON 导入；
4. 尝试其他免费数据源。
