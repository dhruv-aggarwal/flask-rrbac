from datetime import datetime


class ACLRouteMixin(object):
    @property
    def get_rule(self):
        try:
            return self.rule
        except AttributeError:
            raise NotImplementedError('No `route` attribute is present')

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
            return self.deleted_at is not None and \
                self.deleted_at <= datetime.utcnow()
        except AttributeError:
            return False
