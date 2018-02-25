from sqlalchemy.ext.hybrid import hybrid_property


class ACLUserMixin(object):
    def __init__(self):
        if not hasattr(self.__class__, 'roles'):
            self.roles = set()

    def add_role(self, role):
        """Add a role to this user.
        :param role: Role to add.
        """
        self.roles.add(role)

    def add_roles(self, list_of_roles):
        """Add a role to this user.
        :param list_of_roles: Roles to add.
        """
        for role in list_of_roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role

    @hybrid_property
    def get_id(self):
        """Get the unique identifier for a user.
        """
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')
