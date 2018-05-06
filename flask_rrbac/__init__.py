# -*-coding: utf-8
"""
    flaskext.roleroutebasedacl
    ~~~~~~~~~~~~~
    Adds Role-Route-based Access Control modules to application
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
import re
from .defaults import *

__all__ = [
    'RoleRouteBasedACL',
    'ACLRoleMixin',
    'ACLRoleRouteMapMixin',
    'ACLRouteMixin',
    'ACLUserMixin',
    'ACLUserRoleMapMixin'
]

connection_stack = _app_ctx_stack or _request_ctx_stack


class _RoleRouteBasedACLState(object):
    '''Records configuration for Flask-RoleRouteBasedACL'''
    def __init__(self, acl, app):
        self.acl = acl
        self.app = app


class RoleRouteBasedACL(object):
    """This class implements role-route-based access control module in Flask.
    There are two way to initialize Flask-RoleRouteBasedACL::
        app = Flask(__name__)
        rrbac = RoleRouteBasedACL(app)
    or::
        rrbac = RoleRouteBasedACL
        def create_app():
            app = Flask(__name__)
            rrbac.init_app(app)
            return app
    :param app: the Flask object
    :param role_model: custom role model
    :param user_model: custom user model
    :param route_model: custom route model
    :param role_route_map_model: custom role route map model
    :param user_role_map_model: custom user role map model
    :param user_loader: custom user loader, used to load current user
    :param auth_failed_hook: called when authorization fails.
    """

    def __init__(self, app=None, **kwargs):
        """Initialize with app."""
        self.set_role_model(kwargs.get('role_model'))
        self.set_user_model(kwargs.get('user_model'))
        self.set_route_model(kwargs.get('route_model'))
        self.set_role_route_map_model(
            kwargs.get('role_route_map_model')
        )
        self.set_user_role_map_model(
            kwargs.get('user_role_map_model')
        )
        self.set_user_loader(
            kwargs.get('user_loader', lambda: current_user)
        )
        self._auth_fail_hook = kwargs.get('auth_failed_hook')

        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """Initialize application in Flask-RRBAC.
        Adds (RRBAC, app) to flask extensions.
        Adds hook to authenticate permission before request.
        :param app: Flask object
        """

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['roleroutebasedacl'] = _RoleRouteBasedACLState(
            self, app
        )

        self.role_route_config = app.config.get(
            'RRBAC_ROLE_ROUTE_MAP', RRBAC_ROLE_ROUTE_MAP
        )
        # self.allow_static = app.config.get(
        #     'RRBAC_ALLOW_STATIC', RRBAC_ALLOW_STATIC
        # )
        self.anonymous_role_name = app.config.get(
            'RRBAC_ANONYMOUS_ROLE', RRBAC_ANONYMOUS_ROLE
        )
        self.method_alternates = self.app.config.get(
            'RRACL_METHOD_ALTERNATES', RRACL_METHOD_ALTERNATES
        )
        # self.static_rules = self.get_static_rules(app.url_map.iter_rules())
        # app.before_request(self._authenticate)

    def as_role_model(self, model_cls):
        """A decorator to set custom model or role.
        :param model_cls: Model of role.
        """
        self._role_model = model_cls
        return model_cls

    def as_route_model(self, model_cls):
        """A decorator to set custom model or route.
        :param model_cls: Model of route.
        """
        self._route_model = model_cls
        return model_cls

    def as_user_model(self, model_cls):
        """A decorator to set custom model or user.
        :param model_cls: Model of user.
        """
        self._user_model = model_cls
        return model_cls

    def as_user_role_map_model(self, model_cls):
        """A decorator to set custom model or user_role_map.
        :param model_cls: Model of user_role_map.
        """
        self._user_role_map_model = model_cls
        return model_cls

    def as_role_route_map_model(self, model_cls):
        """A decorator to set custom model or role_route_map.
        :param model_cls: Model of role_route_map.
        """
        self._role_route_map_model = model_cls
        return model_cls

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
            rrbac.set_user_loader(lambda: current_user)
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
        raise RuntimeError('application not registered on rrbac '
                           'instance and no application bound '
                           'to current context')

    def _authenticate(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            app = self.get_app()
            assert app, INIIALIZATION_ERRORS['app']
            assert self._role_model, INIIALIZATION_ERRORS['role']
            assert self._user_model, INIIALIZATION_ERRORS['user']
            if not self.role_route_config:
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
            method = self.method_alternates.get(request.method, request.method)
            # if self.allow_static and self.is_static_fetch_endpoint(
            #     method,
            #     request.url_rule.rule
            # ):
            #     result = True
            if current_user.is_authenticated():
                result = self._check_permission(
                    method,
                    request.path,
                    current_user,
                    self.role_route_config,
                    anonymous_role_name=self.anonymous_role_name
                )
            else:
                result = self._check_permission(
                    method,
                    request.path,
                    None,
                    self.role_route_config,
                    anonymous_role_name=self.anonymous_role_name
                )
            if not result:
                return self._auth_fail_hook_caller()
            else:
                return f(*args, **kwargs)
        return decorated_function

    # def get_static_rules(rules_iterable):
    #     return [
    #         item.rule for item in rules_iterable
    #         if not item.methods - {'GET', 'HEAD', 'OPTIONS'} and
    #         re.match('.*static*<path:filename>$', item.rule)
    #     ]

    # def is_static_fetch_endpoint(self, method, requested_rule):
    #     if method != 'GET':
    #         return False
    #     for rule in self.static_rules:
    #         if requested_rule == rule:
    #             return True
    #     return False

    def is_rule_matched(self, path, rule_to_match):
        """
        This function matches the incoming path against the user's rules.

        This funtion determines whether the rule selected matches the incoming
        url. If the url matches the specified pattern, the function evaluates
        to True. Else False.

        Inputs:
            :param path: (type: str) the url hit
            :param rule_to_match: (type: str)
            the pattern which the user has access to
        Output:
            Boolean
        """
        regex_object = re.match(rule_to_match, path)
        if not regex_object:
            return False
        return regex_object.group() == path

    def _check_permission_against_config(
        self, method, path, user, role_route_config, anonymous_role_name
    ):
        """
        This function checks whether the user is allowed to access the incoming
        request.

        The following things are evaluated when checking the user mapping:
        1. user role map entry is valid
        2. there is at least 1 route in user role map entries whose regex
        matches the incoming path
        3. the match rule entry and the method of the path are the same

        Returns True when the user is allowed to access that request.
        False otherwise.

        Input:
            :param method: (type: str) Http method of the incoming request
            :param path: (type: str) Path of the incoming request
            :param user: (type: UserMixin) Current user
            :param role_route_config: (type: dict) Dict for role route mapping
            :param anonymous_role_name: (type: str) Name of the Anonymous Role

        Output:
            Boolean
        """
        user_roles = []
        if user:
            user_roles = self._role_model.query.filter(
                self._role_model.is_deleted == (False)
            ).join(
                self._user_role_map_model
            ).filter(
                self._user_role_map_model.is_deleted == (False)
            ).join(
                self._user_model
            ).filter(
                self._user_model.get_id == user.id
            ).with_entities(self._role_model.name).distinct().all()
        user_roles += [(anonymous_role_name,)]
        roles = set([r[0] for r in user_roles])

        for user_role in roles:
            regexes = role_route_config.get(user_role, {}).get(method, [])
            for regex in regexes:
                if self.is_rule_matched(path, regex):
                    return True
        return False

    def _check_permission_against_db(
        self, method, path, user, anonymous_role_name
    ):
        """
        This function checks whether the user is allowed to access the incoming
        request.

        The following things are evaluated when checking the user mapping:
        1. user role map entry is valid
        2. there is at least 1 route in user role map entries whose regex
        matches the incoming path
        3. the match rule entry and the method of the path are the same

        Returns True when the user is allowed to access that request.
        False otherwise.

        Input:
            :param method: (type: str) Http method of the incoming request
            :param path: (type: str) Path of the incoming request
            :param user: (type: UserMixin) Current user
            :param anonymous_role_name: (type: str) Name of the Anonymous Role

        Output:
            Boolean
        """
        all_rules = self._route_model.query.filter(
            self._route_model.get_method == method
        ).join(
            self._role_route_map_model
        ).filter(
            self._role_route_map_model.is_deleted == (False)
        ).join(
            self._role_model
        ).filter(
            self._role_model.is_deleted == (False)
        )
        user_rules = all_rules.filter(
            self._role_model.name == anonymous_role_name
        )
        if user:
            user_rules = all_rules.join(
                self._user_role_map_model
            ).filter(
                self._user_role_map_model.is_deleted == (False)
            ).join(
                self._user_model
            ).filter(
                self._user_model.get_id == user.id
            ).union(user_rules)
        user_rules = \
            user_rules.with_entities(self._route_model.get_rule).distinct()
        for user_rule in user_rules:
            if self.is_rule_matched(path, user_rule[0]):
                return True
        return False

    def _check_permission(
        self, method, path, user, role_route_config={}, anonymous_role_name=''
    ):
        """Return does the current user can access the resource.
        Example::
            @app.route('/some_url', methods=['GET', 'POST'])
            @rrbac._authenticate
            def a_view_func():
                return Response('Blah Blah...')

        :param method: The method wait to check.
        :param path: The incoming request path.
        :param user: user who you need to check. Current user by default.
        :param role_route_config: User provided config for role route mapping.
        :param anonymous_role_name: Role for anonymous users. This should be
        the same as the name of the corresponding role in db/config
        """
        if role_route_config:
            return self._check_permission_against_config(
                method, path, user, role_route_config, anonymous_role_name
            )
        else:
            return self._check_permission_against_db(
                method, path, user, anonymous_role_name
            )
        return False

    def get_app_routes(self, app):
        rule_dict = {}
        for rule in app.url_map.iter_rules():
            rule_dict[rule.rule] = set()
            for method in rule.methods:
                rule_dict[rule.rule].add(
                    self.method_alternates.get(method, method)
                )
        return rule_dict

    def _auth_fail_hook_caller(self):
        """Call the _auth_fail_hook method of the class.
        """
        if self._auth_fail_hook:
            return self._auth_fail_hook()
        else:
            abort(403)
