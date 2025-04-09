print("Starting NLP Toolkit Backend...")

import os
import sys
import threading
import webview
import encodings
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


def initialize_api(window):
    """
    Initialize the API in the background and attach it to the window once ready.
    """
    print("Initializing API...")
    api = Api()
    print("API initialized")
    window._js_api = api


def loading_window():
    window = webview.create_window('Woah dude!', 'https://pywebview.flowrl.com')
    webview.start()


if __name__ == '__main__':
    # loading_window()
    do_debug = not getattr(sys, 'frozen', False)  # Debug mode if not frozen (i.e., not packaged)

    print("Creating window...")
    # Create the window immediately
    window = webview.create_window(
        'NLP4Edu',
        get_entrypoint(),
        js_api=None,  # Start with no API
        width=1000,
        height=750
    )
    print("Window created")

    # Start the API initialization in a separate thread
    api_thread = threading.Thread(target=initialize_api, args=(window,))
    api_thread.daemon = True  # Daemonize thread to exit when the main program exits
    api_thread.start()

    # Start the UI immediately
    #webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.start(debug=do_debug, gui='edgechromium')
