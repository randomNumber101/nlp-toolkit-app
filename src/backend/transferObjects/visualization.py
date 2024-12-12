from abc import abstractmethod
from typing import List


class Visualization:

    def __init__(self, name):
        self.name = name

    def toJson(self):
        return {
            "type": self.name,
            "content": self.serializeContent()
        }

    @abstractmethod
    def serializeContent(self) -> dict | list:
        pass


class MultiVisualization(Visualization):

    def __init__(self, vizList: List[Visualization]):
        super(MultiVisualization, self).__init__("multi")
        self.vizList = vizList


    def serializeContent(self) -> list:
        return [
            viz.toJson() for viz in self.vizList
        ]




class SimpleTextViz(Visualization):

    def __init__(self, content: str):
        self.content = content
        super(SimpleTextViz, self).__init__("simple_text")

    def serializeContent(self) -> dict:
        return {
            "text": self.content
        }


class HTMLViz(Visualization):

    def __init__(self, html: str, css: str = None):
        self.html = html
        self.css = css
        super(HTMLViz, self).__init__("html")

    def serializeContent(self) -> dict:
        return {
            "html": self.html,
            "css": self.css
        }


