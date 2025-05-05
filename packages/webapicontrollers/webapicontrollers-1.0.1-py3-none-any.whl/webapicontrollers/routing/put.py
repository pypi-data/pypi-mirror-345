from .route import Route
from ..enums import HTTPMethodType


class Put(Route):
    def __init__(self, path: str, name: str = None, description: str = None):
        super().__init__(path, HTTPMethodType.PUT, name, description)