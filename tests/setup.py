from flask import Flask, Response
from ..flask_rrbac import (
    RoleRouteBasedACL,
    ACLUserMixin,
    ACLRoleMixin,
    ACLRoleRouteMapMixin,
    ACLRouteMixin,
    ACLUserRoleMapMixin
)
from flask.ext.login import current_user


class Role(ACLRoleMixin):
    def __repr__(self):
        return '<Role name:{}>'.format(self.name)


class User(ACLUserMixin):
    def __repr__(self):
        return '<User roles:{}>'.format(self.roles)


class Route(ACLRouteMixin):
    def __repr__(self):
        return '<Route rule:{}>'.format(self.rule)


class UserRoleMap(ACLUserRoleMapMixin):
    def __repr__(self):
        return '<UserRoleMap user:{}; role:{}>'.format(self.role, self.user)


class RoleRouteMap(ACLRoleRouteMapMixin):
    def __repr__(self):
        return '<RoleRouteMap route:{}; role:{}>'.format(self.route, self.role)


def makeapp(with_factory=False):
    app = Flask(__name__)
    app.debug = True

    if with_factory:
        rrbac = RoleRouteBasedACL(
            user_model=User,
            role_model=Role,
            route_model=Route,
            role_route_map_model=RoleRouteMap,
            user_role_map_model=UserRoleMap,
            user_loader=lambda: current_user
        )
        rrbac.init_app(app)
    else:
        rrbac = RoleRouteBasedACL(
            app,
            user_model=User,
            role_model=Role,
            route_model=Route,
            role_route_map_model=RoleRouteMap,
            user_role_map_model=UserRoleMap,
            user_loader=lambda: current_user
        )

    @app.route('/uncovered_route')
    def index():
        return Response('uncovered_route')

    @app.route('/covered_route', methods=['GET', 'POST'])
    @rrbac._authenticate
    def b():
        return Response('Hello from /b')

    return app
