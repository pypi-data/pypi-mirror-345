class Registry:
    def __init__(self):
        self.routes = []

    def add_route(self, func, path, method, name=None, description=None):
        self.routes.append((func, path, method, name, description))

    def get_routes(self):
        return self.routes
