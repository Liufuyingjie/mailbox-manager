# -*- coding: utf-8 -*-
"""邮箱管家 - 独立桌面程序

打包为单文件 exe 后可直接双击运行，无需 Python 环境。
数据保存在 %APPDATA%\\邮箱管家\\data.json；若 exe 同目录存在 data.json，
则自动使用该目录（便携模式，方便随软件一起搬走）。
"""
import json
import os
import sys
import tempfile

APP_NAME = "邮箱管家"
VERSION = "1.1.0"
# 作者信息（页面右上角的「关于我」按钮会打开这个地址）
GITHUB_USER = "Liufuyingjie"
REPO_NAME = "mailbox-manager"
REPO_URL = "https://github.com/%s/%s" % (GITHUB_USER, REPO_NAME)


# ---------------- 路径 ----------------
def resource_path(name):
    """打包后资源从 _MEIPASS 解压目录取，开发时从脚本目录取。"""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


def app_dir():
    """程序所在目录（exe 所在位置 / 脚本所在位置）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.normpath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def resolve_data_dir():
    """便携模式优先：exe 旁有 data.json 就用它，否则用用户数据目录。"""
    side = os.path.join(app_dir(), "data.json")
    try:
        if os.path.isfile(side):
            return app_dir()
    except Exception:
        pass
    roaming = os.environ.get("APPDATA") or os.path.expanduser("~")
    target = os.path.join(roaming, APP_NAME)
    try:
        os.makedirs(target, exist_ok=True)
    except Exception:
        target = tempfile.gettempdir()
    return target


DATA_DIR = resolve_data_dir()
DATA_FILE = os.path.join(DATA_DIR, "data.json")


# ---------------- 网页接口 ----------------
class Api:
    """暴露给页面调用的接口：读写本地数据文件。"""

    def load(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save(self, text):
        try:
            tmp = DATA_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, DATA_FILE)
            return True
        except Exception:
            return False

    def info(self):
        return {
            "name": APP_NAME,
            "version": VERSION,
            "dataFile": DATA_FILE,
            "author": GITHUB_USER,
            "repo": REPO_URL,
        }

    def open_url(self, url):
        """用系统默认浏览器打开链接（页面里的「关于我」按钮走这里）。"""
        try:
            url = str(url or "").strip()
            # 只放行 http/https，避免被页面里的任意字符串带偏去执行本地程序
            if not (url.startswith("http://") or url.startswith("https://")):
                return False
            import webbrowser
            return bool(webbrowser.open(url))
        except Exception:
            return False

    def open_data_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(DATA_DIR)  # noqa
                return True
        except Exception:
            pass
        return False


# ---------------- 降级与提示 ----------------
def notify(title, msg):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, msg, title, 0x40)
    except Exception:
        pass


def open_in_browser(html, reason=""):
    """没有 WebView2 时，把页面写到临时文件并用默认浏览器打开。"""
    import webbrowser
    try:
        fd, path = tempfile.mkstemp(suffix=".html", prefix="mailbox_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open("file:///" + path.replace("\\", "/"))
        tip = "\n\n提示：浏览器模式下数据保存在浏览器本地，与桌面窗口模式分开。"
        if reason:
            tip += "\n\n技术信息：" + reason
        notify(APP_NAME, "已用默认浏览器打开。" + tip)
    except Exception as e:
        notify(APP_NAME, "打开失败：" + str(e))


def fatal(msg):
    notify(APP_NAME + " - 启动失败", msg)


# ---------------- 主流程 ----------------
def load_html():
    path = resource_path(APP_NAME + ".html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    try:
        html = load_html()
    except Exception as e:
        fatal("缺少页面资源 %s.html，程序可能已损坏。\n\n%s" % (APP_NAME, e))
        return

    try:
        import webview
    except ImportError as e:
        open_in_browser(html, "未找到 pywebview：%s" % e)
        return

    api = Api()
    try:
        webview.create_window(
            APP_NAME,
            html=html,
            js_api=api,
            width=1360,
            height=860,
            min_size=(1024, 660),
            background_color="#F5F7FA",
            text_select=True,
        )
        webview.start(
            icon=resource_path("app.ico"),
            private_mode=False,
            storage_path=os.path.join(DATA_DIR, "webview"),
        )
    except Exception as e:
        open_in_browser(html, "窗口创建失败：%s" % e)


if __name__ == "__main__":
    main()
