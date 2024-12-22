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

    def __init__(self, vizList: List[Visualization], render_type: str = "numbered", tab_names: List[str] = None):
        """
        :param vizList: List of Visualization objects.
        :param render_type: "numbered" or "tabbed".
        :param tab_names: Optional names for the tabs (used only in tabbed view).
        """
        super(MultiVisualization, self).__init__("multi")
        self.vizList = vizList
        self.render_type = render_type
        self.tab_names = tab_names if tab_names else [f"Viz {i+1}" for i in range(len(vizList))]

    def serializeContent(self) -> dict:
        return {
            "visualizations": [viz.toJson() for viz in self.vizList],
            "render_type": self.render_type,
            "tab_names": self.tab_names
        }


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


class PlotlyViz(Visualization):

    def __init__(self, plotly_figure):
        super(PlotlyViz, self).__init__("plotly")
        self.plotly_json = plotly_figure.to_json()

    def serializeContent(self) -> dict:
        return {
            "config": self.plotly_json
        }
