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

    def add_parent(self, parent):
        parent.children.add(self)
        self.parents.add(parent)

    def add_parents(self, *parents):
        """Add parents to this role. Also should override if neccessary.
        Example::
            editor_of_articles = RoleMixin('editor_of_articles')
            editor_of_photonews = RoleMixin('editor_of_photonews')
            editor_of_all = RoleMixin('editor_of_all')
            editor_of_all.add_parents(editor_of_articles, editor_of_photonews)
        :param parents: Parents to add.
        """
        for parent in parents:
            self.add_parent(parent)

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
