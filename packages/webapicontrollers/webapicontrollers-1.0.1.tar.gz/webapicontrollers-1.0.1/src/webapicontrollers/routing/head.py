from .route import Route
from ..enums import HTTPMethodType

class Head(Route):
    def __init__(self, path: str, name: str = None, description: str = None):
        super().__init__(path, HTTPMethodType.HEAD, name, description)