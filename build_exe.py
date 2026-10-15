# -*- coding: utf-8 -*-
"""把 app.py + 邮箱管家.html + app.ico 打包成单文件 exe。"""
import os
import shutil
import sys

import PyInstaller.__main__

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(BASE, "dist")
BUILD = os.path.join(BASE, "build")
EXE_NAME = "邮箱管家"

args = [
    os.path.join(BASE, "app.py"),
    "--name", "MailBoxManager",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--clean",
    "--icon", os.path.join(BASE, "app.ico"),
    "--add-data", os.path.join(BASE, "邮箱管家.html") + os.pathsep + ".",
    "--add-data", os.path.join(BASE, "app.ico") + os.pathsep + ".",
    "--collect-all", "webview",
    "--collect-all", "clr_loader",
    "--collect-all", "pythonnet",
    "--hidden-import", "clr",
    "--hidden-import", "webview.platforms.winforms",
    "--hidden-import", "webview.platforms.edgechromium",
    "--distpath", DIST,
    "--workpath", BUILD,
    "--specpath", BUILD,
]

if __name__ == "__main__":
    PyInstaller.__main__.run(args)
    raw = os.path.join(DIST, "MailBoxManager.exe")
    final = os.path.join(DIST, EXE_NAME + ".exe")
    if os.path.exists(raw):
        if os.path.exists(final):
            os.remove(final)
        shutil.move(raw, final)
    print("BUILD_DONE ->", final, os.path.getsize(final) if os.path.exists(final) else "MISSING")
