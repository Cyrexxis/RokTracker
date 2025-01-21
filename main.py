import os
import sys
import dummy_root
import webview
import getpass

# Import Bottle
from bottle import static_file, Bottle

MAIN_DIR = os.path.join(dummy_root.get_script_root(), "dist", "spa")

print(MAIN_DIR)

app = Bottle()


@app.get("/")  # type: ignore
def index():
    return static_file("index.html", root=MAIN_DIR)


# Static files route
@app.get("/<filename:path>")  # type: ignore
def get_static_files(filename):
    """Get Static files"""
    response = static_file(filename, root=MAIN_DIR)
    if response.status_code == 404:
        return static_file("index.html", root=MAIN_DIR)
    return response


DEBUG = True


class ResHandler:
    window: webview.Window

    def __init__(self, window):
        self.window = window

    def CallJavascript(self, js):
        self.window.evaluate_js(js)
        return ""


class API:
    def __init__(self):
        self.username = getpass.getuser()

    def GetUsername(self):
        return {"user": self.username}

    def TestPython(self):
        window.evaluate_js("console.log('Hello from python')")
        return ""


def WebViewApp():
    api = API()
    global window
    window = webview.create_window(
        "RoK Tracker Suite",
        app,  # type: ignore
        js_api=api,
        width=1285 + 20,
        height=740 + 40,
    )

    webview.start(debug=DEBUG, http_server=True)


if __name__ == "__main__":
    WebViewApp()
