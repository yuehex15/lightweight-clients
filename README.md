# lightweight-clients

基于 **Tauri v2** 的极轻量 Windows 客户端合集，专为低内存设备设计（如小米平板2，2GB RAM）。

**一个仓库管理多个客户端，`apps.json` 是唯一配置来源。**

## 当前客户端

| 客户端 | 目标网站 | 下载 |
|--------|---------|------|
| **MoonTV** | https://tv.zsam.de5.net/ | [下载](https://github.com/yuehex15/lightweight-clients/releases/tag/moontv) |
| **Nodeseek** | https://www.nodeseek.com/ | [下载](https://github.com/yuehex15/lightweight-clients/releases/tag/nodeseek) |
| **Linux.Do** | https://linux.do/ | [下载](https://github.com/yuehex15/lightweight-clients/releases/tag/linuxdo) |

## 添加新客户端

编辑 `apps.json`，添加条目即可：

```json
{
  "name": "myapp",            // 唯一标识，用于 release tag
  "title": "MyApp",           // 显示名称
  "url": "https://example.com/",  // 目标网址
  "width": 1280,              // 窗口宽度
  "height": 720,              // 窗口高度
  "identifier": "com.myapp.client",  // 应用标识
  "icon_color": [100, 200, 50]       // 图标颜色 RGB
}
```

修改后推送，CI 会自动：
1. 生成客户端源码
2. 编译
3. 打包 zip + MSI
4. 发布到 `https://github.com/yuehex15/lightweight-clients/releases/tag/你的name`

## 修改域名

在 `apps.json` 中找到对应条目的 `url` 字段，修改后推送即可。**不需要改代码。**

## 功能特性

- 🪶 **极低内存占用**：~50-100MB（WebView2 系统渲染）
- 📦 **安装包**：zip 含 exe + 配置文件，另有 MSI 安装包
- 🎨 **自动图标**：根据 `icon_color` 生成不同颜色图标
- ⚙️ **运行时配置**：解压后 `settings.ini` 可设代理/禁 GPU 等
- 🔄 **自动覆盖**：每次推送覆盖同一 Release，不产生历史版本