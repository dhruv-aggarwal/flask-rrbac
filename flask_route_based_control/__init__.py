# -*-coding: utf-8
"""
    flaskext.rbac
    ~~~~~~~~~~~~~
    Adds Role-based Access Control modules to application
"""

from functools import wraps

from flask import request, abort, _request_ctx_stack

try:
    from flask import _app_ctx_stack
except ImportError:
    _app_ctx_stack = None

try:
    from flask_login import (
        current_user, AnonymousUserMixin as anonymous_model
    )
except ImportError:
    current_user, anonymous_model = None, None

from .models import (
    ACLRoleMixin, ACLRoleRouteMapMixin, ACLRouteMixin, ACLUserMixin,
    ACLUserRoleMapMixin
)
from .messages import INIIALIZATION_ERRORS

__all__ = [
    'RouteBasedACL',
    'ACLRoleMixin',
    'ACLRoleRouteMapMixin',
    'ACLRouteMixin',
    'ACLUserMixin',
    'ACLUserRoleMapMixin'
]

connection_stack = _app_ctx_stack or _request_ctx_stack


class _RouteBasedACLState(object):
    '''Records configuration for Flask-RouteBasedACL'''
    def __init__(self, acl, app):
        self.acl = acl
        self.app = app


class RouteBasedACL(object):
    """This class implements role-based access control module in Flask.
    There are two way to initialize Flask-RBAC::
        app = Flask(__name__)
        rbac = RBAC(app)
    or::
        rbac = RBAC
        def create_app():
            app = Flask(__name__)
            rbac.init_app(app)
            return app
    :param app: the Flask object
    :param role_model: custom role model
    :param user_model: custom user model
    :param user_loader: custom user loader, used to load current user
    :param auth_failed_hook: called when authorization fails.
    """

    def __init__(self, app=None, **kwargs):
        """Initialize with app."""
        self._role_model = kwargs.get('role_model', ACLRoleMixin)
        self._user_model = kwargs.get('user_model', ACLUserMixin)
        self._route_model = kwargs.get('route_model', ACLRouteMixin)
        self._role_route_map_model = kwargs.get(
            'role_route_map_model', ACLRoleRouteMapMixin
        )
        self._user_role_map_model = kwargs.get(
            'user_role_map_model', ACLUserRoleMapMixin
        )
        self._auth_fail_hook = kwargs.get('auth_failed_hook')

        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """Initialize application in Flask-RBAC.
        Adds (RBAC, app) to flask extensions.
        Adds hook to authenticate permission before request.
        :param app: Flask object
        """

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['acl'] = _RouteBasedACLState(self, app)

        # self.acl.allow(anonymous, 'GET', app.view_functions['static'])
        # app.before_first_request(self._setup_acl)

        # app.before_request(self._authenticate)

    def set_role_model(self, model_class):
        """Decorator to set a custom model for roles.
        :param model_class: Model of role.
        """
        self._role_model = model_class

    def set_route_model(self, model_class):
        """Decorator to set a custom model for routes.
        :param model_class: Model of route.
        """
        self._route_model = model_class

    def set_user_model(self, model_class):
        """Decorator to set a custom model for users.
        :param model_class: Model of user.
        """
        self._user_model = model_class

    def set_user_role_map_model(self, model_class):
        """Decorator to set a custom model for user_role_map.
        :param model_class: Model of user_role_map.
        """
        self._user_role_map_model = model_class

    def set_role_route_map_model(self, model_class):
        """Decorator to set a custom model for role_route_map.
        :param model_class: Model of role_route_map.
        """
        self._role_route_map_model = model_class

    def set_user_loader(self, loader):
        """
        Set the function used to load the user in context.
        E.g.
            from flask_login import current_user
            rbacl.set_user_loader(lambda: current_user)
        :param loader: Current user function.
        """
        self._user_loader = loader

    def set_auth_fail_hook(self, auth_fail_hook):
        """Set auth_fail_hook which called when Authorization fails
        If you haven't set any hook, Flask-RBACL will call::
            abort(403)
        :param auth_fail_hook: Hook function
        """
        self._auth_fail_hook = auth_fail_hook

    def get_app(self, reference_app=None):
        """Helper method that implements the logic to look up an application.
        """
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        ctx = connection_stack.top
        if ctx is not None:
            return ctx.app
        raise RuntimeError('application not registered on rbac '
                           'instance and no application bound '
                           'to current context')

    def _authenticate(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            app = self.get_app()
            assert app, INIIALIZATION_ERRORS['app']
            assert self._role_model, INIIALIZATION_ERRORS['role']
            assert self._user_model, INIIALIZATION_ERRORS['user']
            assert self._route_model, INIIALIZATION_ERRORS['route']
            assert self._role_route_map_model, \
                INIIALIZATION_ERRORS['role_route_map']
            assert self._user_role_map_model, \
                INIIALIZATION_ERRORS['user_role_map']
            assert self._user_loader, INIIALIZATION_ERRORS['user_loader']

            current_user = self._user_loader()

            # Compatible with flask-login anonymous user
            if hasattr(current_user, '_get_current_object'):
                current_user = current_user._get_current_object()

            if current_user is not None and not isinstance(
                current_user, (self._user_model, anonymous_model)
            ):
                raise TypeError("{user} is not an instance of {model}".format(
                    current_user, self._user_model.__class__
                ))

            endpoint = request.url_rule.endpoint
            method = request.method
            if current_user.is_authenticated:
                result = self._check_permission(method, endpoint, current_user)
                if not result:
                    return self._deny_hook()
            return f(*args, **kwargs)
        return decorated_function

    def _check_permission(self, method, endpoint, user):
        """Return does the current user can access the resource.
        Example::
            @app.route('/some_url', methods=['GET', 'POST'])
            @rbac._authenticate
            def a_view_func():
                return Response('Blah Blah...')

        :param method: The method wait to check.
        :param endpoint: The application endpoint.
        :param user: user who you need to check. Current user by default.
        """
        return self._route_model.query.join(
            self._role_route_map_model
        ).filter(
            self._role_route_map_model.is_deleted.is_(None)
        ).join(
            self._role_model
        ).filter(
            self._role_model.is_deleted.is_(None)
        ).join(
            self._user_role_map_model
        ).filter(
            self._user_role_map_model.is_deleted.is_(None)
        ).join(
            self._user_model
        ).filter(
            self._user_model.id == current_user.id
        ).filter(
            self._route_model.name == request.url_rule.endpoint
        ).filter(
            self._route_model.method == request.method
        ).count() > 0

    def _deny_hook(self):
        if self.permission_failed_hook:
            return self.permission_failed_hook()
        else:
            abort(403)
