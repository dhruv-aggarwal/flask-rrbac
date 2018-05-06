from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, case


class ACLRoleMixin(object):
    def __init__(self):
        if not hasattr(self.__class__, 'routes'):
            self.routes = set()

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

    @property
    def get_routes(self):
        for route in self.routes:
            yield route
