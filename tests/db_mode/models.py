from . import rrbac, db, login_manager
from flask_rrbac import (
    ACLUserMixin,
    ACLRoleMixin,
    ACLRoleRouteMapMixin,
    ACLRouteMixin,
    ACLUserRoleMapMixin
)
from flask.ext.login import UserMixin


@rrbac.as_role_model
class Role(db.Model, ACLRoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)


@rrbac.as_user_model
class User(db.Model, ACLUserMixin, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)


@rrbac.as_route_model
class Route(db.Model, ACLRouteMixin):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    method = db.Column(db.String(10), nullable=False)
    rule = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)


@rrbac.as_user_role_map_model
class UserRoleMap(db.Model, ACLUserRoleMapMixin):
    __tablename__ = 'user_role_map'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    user = db.relationship(
        'User', backref=db.backref(
            'user_role_map_entries',
            cascade='all,delete-orphan'
        )
    )
    role = db.relationship(
        'Role', backref=db.backref(
            'user_role_map_entries',
            cascade='all,delete-orphan'
        )
    )


@rrbac.as_role_route_map_model
class RoleRouteMap(db.Model, ACLRoleRouteMapMixin):
    __tablename__ = 'role_route_map'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    route_id = db.Column(
        db.Integer,
        db.ForeignKey('routes.id'),
        nullable=False
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    route = db.relationship(
        'Route', backref=db.backref(
            'role_route_map_entries',
            cascade='all,delete-orphan'
        )
    )
    role = db.relationship(
        'Role', backref=db.backref(
            'role_route_map_entries',
            cascade='all,delete-orphan'
        )
    )


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
