from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case, func


class ACLRouteMixin(object):
    @hybrid_property
    def get_rule(self):
        try:
            return self.rule
        except AttributeError:
            raise NotImplementedError('No `route` attribute is present')

    @hybrid_property
    def get_id(self):
        try:
            return self.id
        except AttributeError:
            raise NotImplementedError('No `id` attribute is present')

    @hybrid_property
    def get_method(self):
        try:
            return self.method
        except AttributeError:
            raise NotImplementedError('No `method` attribute is present')

    @hybrid_property
    def is_deleted(self):
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
