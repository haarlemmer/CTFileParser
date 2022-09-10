# CTFile Auto Download
[![Pylint](https://github.com/haarlemmer/CTFile-Auto-Download/actions/workflows/pylint.yml/badge.svg)](https://github.com/haarlemmer/CTFile-Auto-Download/actions/workflows/pylint.yml)

基于Python的城通网盘解析器, 避免等待下载文件耗费大量时间

## To-Do
- [X] 分享读取
    - [X] 单层文件夹分享读取
    - [X] 多层文件夹分享读取
    - [X] 单文件分享读取
- [X] 下载直链生成
- [ ] 自动顺序下载

# Demo 演示

## 演示用分享链接

|      类型     |                        链接                             | 密码 |
|---------------|--------------------------------------------------------|------|
|  标准分享链接  |  https://url21.ctfile.com/d/37740821-50083730-3d8dc1   | 8854 |
| 带密码分享链接 |https://url21.ctfile.com/d/37740821-50083730-3d8dc1?p=8854| 8854 |
|可自动填充的带密码链接|https://url88.ctfile.com/f/15911488-610504385-f9edda?p=1234|1234|
带密码分享链接在某些情况下会自动填充密码, 我目前没有在自己的账号上触发成功, 目前**暂不支持解析**, 请手动删除 `?p=xxxx` 后解析


# Issues 问题

## Known Issues 已知问题
- [ ] \[ Issues [#2](https://github.com/haarlemmer/CTFile-Auto-Download/issues/2) \]读取包含大量文件的分享时, 爬虫会触发城通的风控出现HTTP 429错误, IP被封
- [X] 城通API改版导致无法解析

## Report Issues 提交问题
你可以在 [Issues](https://github.com/haarlemmer/CTFile-Auto-Download/issues) 提交问题

## Sponsors

[<img alt="JetBrains" height="216.8" src="https://github.com/haarlemmer/CTFile-Auto-Download/blob/master/sponsors/jetbrains.png?raw=true" width="200"/>](https://jb.gg/OpenSource)