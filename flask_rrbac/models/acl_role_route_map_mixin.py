from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, case


class ACLRoleRouteMapMixin(object):
    def __init__(self):
        if not hasattr(self.__class__, 'role'):
            self.role = None
        if not hasattr(self.__class__, 'route'):
            self.route = None

    @property
    def get_role(self):
        """
        Get the role attached to this entry. This has to be implemented.
        """
        try:
            return self.role
        except AttributeError:
            raise NotImplementedError('No `role` attribute is present')

    @hybrid_property
    def get_id(self):
        """
        Get the unique identifier for this entry. This has to be implemented.
        """
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')

    @property
    def get_route(self):
        """
        Get the route attached to this entry. This has to be implemented.
        """
        try:
            return self.route
        except AttributeError:
            raise NotImplementedError('No `route` attribute is present')

    @hybrid_property
    def is_deleted(self):
        """
        Check if this entry is active or not
        An entry is active when the following conditions are met:
            1. deleted_at is empty (None). This means that this entry will not
            expire
            2. deleted_at is in the future. This means that the entry
            has not already expired
        """
        try:
            if self.deleted_at is None:
                return False
            elif self.deleted_at > datetime.utcnow():
                return False
            else:
                return True
        except AttributeError:
            return False

    @is_deleted.expression
    def is_deleted(cls):
        try:
            return case([
                (cls.deleted_at == None, False),
                (cls.deleted_at > func.now(), False)
            ], else_=True)
        except AttributeError:
            return False
