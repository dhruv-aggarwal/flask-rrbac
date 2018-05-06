from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, case


class ACLUserRoleMapMixin(object):
    def __init__(self):
        if not hasattr(self.__class__, 'role'):
            self.role = None
        if not hasattr(self.__class__, 'user'):
            self.user = None

    @property
    def get_user(self):
        """Get the user attached to this entry."""
        try:
            return self.user
        except AttributeError:
            raise NotImplementedError('No `user` attribute is present')

    @hybrid_property
    def get_id(self):
        """Get the unique identifier for a map.
        """
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')

    @property
    def get_role(self):
        """Get the role attached to this entry."""
        try:
            return self.role
        except AttributeError:
            raise NotImplementedError('No `role` attribute is present')

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
