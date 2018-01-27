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
        for role in list_of_roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role
