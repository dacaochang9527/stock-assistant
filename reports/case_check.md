# 真实案例验证记录

更新时间：2026-05-24

## 目标案例

- 正面教材：佳力图 603912，D2 日期按用户资料记为 2022-12-21。
- 反面教材：天安新材 603725，D2 日期按用户资料记为 2023-07-28。

## 当前状态

已实现 `stock_assistant.case_check`：

```bash
NO_PROXY='*' no_proxy='*' .venv/bin/python -m stock_assistant.case_check --case all
```

当前运行结果：

```text
603912 佳力图 2022-12-21: 数据获取失败：ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
603725 天安新材 2023-07-28: 数据获取失败：ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

## 判断

- akshare 已安装成功，且 `stock_info_a_code_name()` 能拉到 A 股代码列表。
- 东方财富历史 K 线接口 `push2his.eastmoney.com` 当前连接被远端断开；即使设置 `NO_PROXY='*'` 绕过 macOS 系统代理，也仍然失败。
- 因此项目代码已具备案例验证入口，但当前网络/接口状态暂时无法完成真实历史 K 线验证。

## 后续处理

可选方案：

1. 换一个网络环境后重试；
2. 改用 tushare，需要 token；
3. 手工下载两个案例的历史日线 CSV 放入 `data/raw/` 后用 CSV provider 验证；
4. 为 akshare adapter 增加备用接口。
