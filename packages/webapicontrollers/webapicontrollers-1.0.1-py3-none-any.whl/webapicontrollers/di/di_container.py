class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DIContainer(metaclass=Singleton):
    def __init__(self, service=None):
        self.services = {}
        if service:
            self.services[type(service)] = service

    def register(self, service):
        self.services[type(service)] = service
        return service

    def get(self, service_type):
        return self.services.get(service_type)
