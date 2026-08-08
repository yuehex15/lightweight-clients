#!/usr/bin/env python3
"""
从 apps.json 配置文件生成各客户端源码。
用法: python3 build.py
"""
import json
import os
import shutil
import struct
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "template")
APPS_JSON = os.path.join(ROOT, "apps.json")
OUT = os.path.join(ROOT, "apps")


def create_png(width, height, pixels):
    def wc(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            raw += struct.pack('BBBB', *pixels[y * width + x])
    return (b'\x89PNG\r\n\x1a\n'
            + wc(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + wc(b'IDAT', zlib.compress(raw)) + wc(b'IEND', b''))


def make_icon(size, color):
    """生成圆角矩形渐变图标"""
    r0, g0, b0 = color
    cr = int(size * 0.18)
    cx, cy = size // 2, size // 2
    pixels = []
    for y in range(size):
        for x in range(size):
            def in_rr(px, py, s, r):
                if px < r and py < r: return (px-r)**2 + (py-r)**2 <= r**2
                if px >= s-r and py < r: return (px-(s-r))**2 + (py-r)**2 <= r**2
                if px < r and py >= s-r: return (px-r)**2 + (py-(s-r))**2 <= r**2
                if px >= s-r and py >= s-r: return (px-(s-r))**2 + (py-(s-r))**2 <= r**2
                return True
            if in_rr(x, y, size, cr):
                d = ((x-cx)**2 + (y-cy)**2)**0.5
                f = 1.0 - (d / cx) * 0.15
                pixels.append((min(255,int(r0*f)), min(255,int(g0*f)), min(255,int(b0*f)), 255))
            else:
                pixels.append((0,0,0,0))
    return create_png(size, size, pixels)


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

    # 生成图标源文件
    icon_png = make_icon(256, app["icon_color"])
    with open(os.path.join(src_tauri, "icons", "icon.png"), "wb") as f:
        f.write(icon_png)
    print(f"  ✓ 生成图标 icon.png")

    # 生成源码文件
    subs = {
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