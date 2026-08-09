#!/usr/bin/env python3
"""
从 apps.json 配置文件生成各客户端源码。
用法: python3 build.py
"""
import json
import os
import shutil
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template")
APPS_JSON = os.path.join(ROOT, "apps.json")
OUT = os.path.join(ROOT, "apps")
DEFAULT_ICON = os.path.join(TEMPLATE, "icons", "icon.png")


def download_icon(url, dest):
    """下载图标到目标路径"""
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"  ⚠ 下载图标失败: {e}")
        return False


def gen_settings_ini(app):
    return f"""# {app['title']} 客户端配置文件
# 放在 exe 同级目录下，程序启动时自动读取

# 域名默认值在仓库 apps.json 中配置，修改后重新构建。
# 此文件仅用于运行时代理/优化设置。

# 代理模式：system / direct / custom
proxy_mode = system

# 自定义代理（仅 custom 模式）
# custom_proxy = 127.0.0.1:10809

# 禁用 GPU 加速（省内存，默认开启）
disable_gpu = true

# JS 堆内存上限（MB，默认 128）
max_js_heap = 128
"""


def gen_readme(app):
    return f"""# {app['title']} 轻量 Windows 客户端

基于 **Tauri v2** 的极轻量客户端，专为低内存设备设计。

## 📥 下载

从 [Releases](https://github.com/yuehex15/lightweight-clients/releases) 下载 `{app['title']}-Windows-x64.zip`。

## 📝 使用

1. 解压 zip 到任意目录
2. 运行 `{app['title']}.exe`
3. 登录使用

## 🔧 修改域名

域名默认值在仓库根目录 `apps.json` 中，编辑对应条目的 `url` 字段后推送，CI 会自动重新构建。

## ⚙️ 运行时配置

同目录 `settings.ini` 可自定义代理模式（system/direct/custom）、禁用 GPU、JS 堆内存限制。

## 🖥 最低配置：Windows 10/11 x64, 1GB+ RAM
"""


def generate_app(app):
    name = app["name"]
    title = app["title"]
    out_dir = os.path.join(OUT, name)
    src_tauri = os.path.join(out_dir, "src-tauri")

    # 清理并重建
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(os.path.join(src_tauri, "src"), exist_ok=True)
    os.makedirs(os.path.join(src_tauri, "capabilities"), exist_ok=True)
    os.makedirs(os.path.join(src_tauri, "icons"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "dist"), exist_ok=True)

    # 复制所有图标文件
    icons_template = os.path.join(TEMPLATE, "icons")
    icons_dest = os.path.join(src_tauri, "icons")
    if os.path.exists(icons_template):
        for f in os.listdir(icons_template):
            shutil.copy2(os.path.join(icons_template, f), os.path.join(icons_dest, f))
    # 如果设置了 icon_url，下载并覆盖源图
    icon_url = app.get("icon_url")
    if icon_url:
        icon_path = os.path.join(icons_dest, "icon.png")
        print(f"  🔽 下载图标: {icon_url}")
        if download_icon(icon_url, icon_path):
            print(f"  ✓ 图标已下载")
        else:
            print(f"  ✓ 使用默认图标（下载失败）")
    else:
        print(f"  ✓ 使用默认图标")

    # 生成源码文件
    subs = {
        # 双大括号占位符必须在前（否则单大括号会先匹配破坏它们）
        "{{TITLE}}": title,
        "{{IDENTIFIER}}": app["identifier"],
        "{{WIDTH}}": str(app.get("width", 1280)),
        "{{HEIGHT}}": str(app.get("height", 720)),
        # 单大括号占位符
        "{TITLE}": title,
        "{NAME}": name,
        "{NAME_UPPER}": name.upper(),
        "{IDENTIFIER}": app["identifier"],
        "{URL}": app["url"],
        "{WIDTH}": str(app.get("width", 1280)),
        "{HEIGHT}": str(app.get("height", 720)),
    }

    def sub(content):
        for k, v in subs.items():
            content = content.replace(k, v)
        return content

    # lib.rs
    with open(os.path.join(TEMPLATE, "lib.rs"), encoding="utf-8") as f:
        content = sub(f.read())
    with open(os.path.join(src_tauri, "src", "lib.rs"), "w", encoding="utf-8") as f:
        f.write(content)

    # main.rs
    with open(os.path.join(TEMPLATE, "main.rs"), encoding="utf-8") as f:
        content = sub(f.read())
    with open(os.path.join(src_tauri, "src", "main.rs"), "w", encoding="utf-8") as f:
        f.write(content)

    # Cargo.toml
    with open(os.path.join(TEMPLATE, "Cargo.toml"), encoding="utf-8") as f:
        content = sub(f.read())
    with open(os.path.join(src_tauri, "Cargo.toml"), "w", encoding="utf-8") as f:
        f.write(content)

    # build.rs
    shutil.copy(os.path.join(TEMPLATE, "build.rs"), os.path.join(src_tauri, "build.rs"))

    # tauri.conf.json
    with open(os.path.join(TEMPLATE, "tauri.conf.json"), encoding="utf-8") as f:
        content = sub(f.read())
    with open(os.path.join(src_tauri, "tauri.conf.json"), "w", encoding="utf-8") as f:
        f.write(content)

    # capabilities
    shutil.copy(os.path.join(TEMPLATE, "capabilities.json"),
                os.path.join(src_tauri, "capabilities", "default.json"))

    # dist/index.html
    with open(os.path.join(TEMPLATE, "index.html"), encoding="utf-8") as f:
        content = sub(f.read())
    with open(os.path.join(out_dir, "dist", "index.html"), "w", encoding="utf-8") as f:
        f.write(content)

    # settings.ini
    with open(os.path.join(out_dir, "settings.ini"), "w", encoding="utf-8") as f:
        f.write(gen_settings_ini(app))

    # README.md
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(gen_readme(app))

    # .gitignore
    with open(os.path.join(out_dir, ".gitignore"), "w") as f:
        f.write("src-tauri/target/\nsrc-tauri/gen/\nnode_modules/\n")

    print(f"  ✓ 生成 {name} ({title}) 源码")


def main():
    with open(APPS_JSON, encoding="utf-8") as f:
        apps = json.load(f)

    print(f"共 {len(apps)} 个应用:")
    for app in apps:
        generate_app(app)
    print(f"\n全部生成完成 → {OUT}/")


if __name__ == "__main__":
    main()