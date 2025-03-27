from typing import Dict, Any, Optional, List


from backend.types.params import Parameter


class Payload(Dict[str, Any]):

    def __init__(self, values: Optional[Dict[str, Any]] = None, link_to_parent: Optional['Payload'] = None):
        super().__init__()
        self.link_to_parent = link_to_parent

        # Initialize protected attributes
        if not link_to_parent:
            super().__setitem__('visualizations', [])

        if values is not None:
            for k, v in values.items():
                super().__setitem__(k, v)  # Correctly set attribute based on key

    def __setitem__(self, key: str, value: Any):
        if self.link_to_parent is not None:
            self.link_to_parent[key] = value
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        if key == "visualizations" and self.link_to_parent:
            return self.link_to_parent[key]
        if self.link_to_parent and key not in self and key in self.link_to_parent:
            raise ValueError(
                f"{key} is not in this partial view, but in parent. You might have forgotten to declare it as input.")
        return super().__getitem__(key)

    def __setattr__(self, key: str, value: Any):
        if key in {'link_to_parent'}:
            super().__setattr__(key, value)
            return
        self[key] = value

    def __getattr__(self, key: str) -> Any:
        if key in {'link_to_parent'}:
            super().__getattribute__(key)

        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'Payload' object has no attribute '{key}'")

    def popVisualizations(self):
        visualizations = self['visualizations']
        self['visualizations'] = []
        return visualizations

    def addVisualization(self, viz: Any):
        self['visualizations'].append(viz)

    def partialView(self, params: List[Parameter]) -> 'Payload':
        partial_values = {param.name: param.type.parse(self[param.name]) for param in params}
        return Payload(partial_values, link_to_parent=self)
