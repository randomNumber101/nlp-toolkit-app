import os
import sys
import threading
import webview
from backend.Api import Api


def get_entrypoint():

    if '--dev' in sys.argv:
        print("Running backend in dev mode")
        return 'http://localhost:5173'

    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists('../gui/index.html'):
        return '../gui/index.html'
    if exists('../Resources/gui/index.html'):
        return '../Resources/gui/index.html'
    if exists('./gui/index.html'):
        return './gui/index.html'

    raise Exception('No index.html found')


def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():
                while not stopped.wait(interval):
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True
            t.start()
            return stopped

        return wrapper
    return decorator


entry = get_entrypoint()

if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'NLP Toolkit',
        entry,
        js_api=api,
        width=1000,
        height=750
    )
    webview.start(debug=True)
