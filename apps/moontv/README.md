# MoonTV 轻量 Windows 客户端

基于 **Tauri v2** 的极轻量客户端，专为低内存设备设计。

## 📥 下载

从 [Releases](https://github.com/yuehex15/lightweight-clients/releases) 下载 `MoonTV-Windows-x64.zip`。

## 📝 使用

1. 解压 zip 到任意目录
2. 运行 `MoonTV.exe`
3. 登录使用

## 🔧 修改域名

域名默认值在仓库根目录 `apps.json` 中，编辑对应条目的 `url` 字段后推送，CI 会自动重新构建。

## ⚙️ 运行时配置

同目录 `settings.ini` 可自定义代理模式（system/direct/custom）、禁用 GPU、JS 堆内存限制。

## 🖥 最低配置：Windows 10/11 x64, 1GB+ RAM
