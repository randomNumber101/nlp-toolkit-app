import sys
import os
import shutil


class Paths:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # One-file mode: resources are in sys._MEIPASS
                internal_path = sys._MEIPASS
                if sys.platform == "darwin":  # macOS
                    base_path = os.path.expanduser("~/Library/Application Support/NLP Toolkit/")
                elif sys.platform == "win32":  # Windows
                    base_path = os.path.join(os.getenv("APPDATA"), "NLP Toolkit")
                else:  # Linux
                    base_path = os.path.expanduser("~/.local/share/NLP Toolkit")
                self.storage = os.path.join(base_path, "storage")
                self.copy_to_storage(os.path.join(internal_path, "storage"))
            else:
                # One-directory mode: resources are in _internal relative to executable
                base_path = os.path.join(os.path.dirname(sys.executable), '_internal')
            self.storage = os.path.join(base_path, 'storage')
        else:
            # Development mode: use relative path
            self.storage = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage"))

        # Define subdirectories (same as before)
        self.pipelines = os.path.join(self.storage, "pipelines")
        self.steps = os.path.join(self.storage, "steps")
        self.runs = os.path.join(self.storage, "runs")
        self.cache = os.path.join(self.storage, "cache")

        os.makedirs(self.pipelines, exist_ok=True)
        os.makedirs(self.steps, exist_ok=True)
        os.makedirs(self.runs, exist_ok=True)
        os.makedirs(self.cache, exist_ok=True)

    def copy_to_storage(self, embedded_storage):
        if not os.path.exists(embedded_storage):
            raise FileNotFoundError(f"Embedded storage not found at: {embedded_storage}")

        if not os.path.exists(self.storage):
            try:
                # For Python >=3.8, use dirs_exist_ok
                shutil.copytree(embedded_storage, self.storage, dirs_exist_ok=True)
            except AttributeError:
                # Fallback for Python <3.8
                if os.path.exists(self.storage):
                    shutil.rmtree(self.storage)
                shutil.copytree(embedded_storage, self.storage)


PATHS = Paths()