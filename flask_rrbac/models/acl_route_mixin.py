class ACLRouteMixin(object):
    @property
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
    def get_method(self):
        try:
            return self.method
        except AttributeError:
            raise NotImplementedError('No `method` attribute is present')

    @property
    def is_deleted(self):
        try:
            return self.deleted_at is not None
        except AttributeError:
            return False
