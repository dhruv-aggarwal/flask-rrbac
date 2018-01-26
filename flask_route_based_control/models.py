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
            raise NotImplementedError('No `deleted_at` attribute is present')


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
    def get_parents(self):
        for parent in self.parents:
            yield parent
            for grandparent in parent.get_parents:
                yield grandparent

    def add_parents(self, list_of_parents):
        self.parents.update(list_of_parents)

    @property
    def get_children(self):
        for child in self.children:
            yield child
            for grandchild in child.get_children:
                yield grandchild

    def add_children(self, list_of_children):
        self.children.update(list_of_children)

    @property
    def get_eligible_routes(self):
        for route in self.routes:
            yield route
        children = self.get_children
        for child in children:
            for route in child.routes:
                yield route

class ACLUserMixin(object):

    def __init__(self):
        if not hasattr(self.__class__, 'roles'):
            self.roles = set()

    def add_roles(self, list_of_roles):
        self.roles.update(list_of_roles)

    def get_roles(self):
        for role in self.roles:
            yield role


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
