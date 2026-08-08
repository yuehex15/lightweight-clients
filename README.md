# lightweight-clients

基于 **Tauri v2** 的极轻量 Windows 客户端，专为低内存设备设计（如小米平板2，2GB RAM）。

一个仓库管理多个客户端，通过 `apps.json` 配置。

## 当前客户端

| 客户端 | 目标网站 | 标签 | 下载 |
|--------|---------|------|------|
| **MoonTV** | https://tv.zsam.de5.net/ | `moontv` | [下载](https://github.com/yuehex15/lightweight-clients/releases/tag/moontv) |
| **Nodeseek** | https://www.nodeseek.com/ | `nodeseek` | [下载](https://github.com/yuehex15/lightweight-clients/releases/tag/nodeseek) |
| **Linux.Do** | https://linux.do/ | `linuxdo` | [下载](https://github.com/yuehex15/lightweight-clients/releases/tag/linuxdo) |

## 添加/修改客户端

编辑 `apps.json`，添加或修改条目即可：

```json
{
  "name": "myapp",
  "title": "MyApp",
  "url": "https://example.com/",
  "width": 1280,
  "height": 720,
  "identifier": "com.myapp.client",
  "icon_color": [100, 200, 50]
}
```

修改后推送，GitHub Actions 自动构建并更新 Release。

## 本地开发

```bash
pip3 install -r requirements.txt
python3 build.py       # 生成所有客户端源码
cd apps/moontv         # 进入某客户端目录
npx tauri icon src-tauri/icons/icon.png  # 生成图标
cargo tauri dev        # 运行开发模式