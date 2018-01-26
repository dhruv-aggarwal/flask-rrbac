class ACLUserRoleMapMixin(object):
    @property
    def get_user(self):
        try:
            return self.user
        except AttributeError:
            raise NotImplementedError('No `user` attribute is present')

    @property
    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')

    @property
    def get_role(self):
        try:
            return self.role
        except AttributeError:
            raise NotImplementedError('No `role` attribute is present')

    @property
    def is_deleted(self):
        try:
            return self.deleted
        except AttributeError:
            raise NotImplementedError('No `deleted` attribute is present')
