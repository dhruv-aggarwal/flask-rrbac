class ACLRoleMixin(object):
    def __init__(self):
        if not hasattr(self.__class__, 'routes'):
            self.routes = set()

    @property
    def is_deleted(self):
        try:
            return self.deleted_at is not None
        except AttributeError:
            return False

    @property
    def get_routes(self):
        for route in self.routes:
            yield route
