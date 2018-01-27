class ACLRoleRouteMapMixin(object):
    @property
    def get_role(self):
        try:
            return self.role
        except AttributeError:
            raise NotImplementedError('No `role` attribute is present')

    @property
    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')

    @property
    def get_route(self):
        try:
            return self.route
        except AttributeError:
            raise NotImplementedError('No `route` attribute is present')

    @property
    def is_deleted(self):
        try:
            return self.deleted_at is not None
        except AttributeError:
            raise NotImplementedError('No `deleted_at` attribute is present')
