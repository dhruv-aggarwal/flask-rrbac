class ACLRoleMixin(object):
    def __init__(self):
        if not hasattr(self.__class__, 'parents'):
            self.parents = set()
        if not hasattr(self.__class__, 'children'):
            self.children = set()
        if not hasattr(self.__class__, 'routes'):
            self.routes = set()

    def get_name(self):
        try:
            return self.name
        except AttributeError:
            raise NotImplementedError('No `name` attribute is present')

    @property
    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')

    @property
    def is_deleted(self):
        try:
            return self.deleted_at is not None
        except AttributeError:
            raise NotImplementedError('No `deleted_at` attribute is present')

    @property
    def get_eligible_routes(self):
        for route in self.routes:
            yield route
